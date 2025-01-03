import json
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import glob
import os
from collections import defaultdict
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak
import io

def analyze_timestamp_gaps(timestamps):
    if not timestamps:
        return {
            'max_gap': 0,
            'min_gap': 0,
            'mean_gap': 0,
            'std_gap': 0
        }

    timestamps = sorted(timestamps)
    gaps = np.diff(timestamps)

    return {
        'max_gap': float(np.max(gaps)) if len(gaps) > 0 else 0,
        'min_gap': float(np.min(gaps)) if len(gaps) > 0 else 0,
        'mean_gap': float(np.mean(gaps)) if len(gaps) > 0 else 0,
        'std_gap': float(np.std(gaps)) if len(gaps) > 0 else 0
    }

def analyze_system_status(heartbeats):
    status_counts = defaultdict(int)
    mode_counts = defaultdict(int)

    for hb in heartbeats:
        if 'system_status' in hb:
            status_counts[hb['system_status']] += 1
        if 'custom_mode' in hb:
            mode_counts[hb['custom_mode']] += 1

    return {
        'status_distribution': dict(status_counts),
        'mode_distribution': dict(mode_counts),
        'total_heartbeats': len(heartbeats)
    }

def analyze_source_distribution(messages):
    sources = defaultdict(int)
    for msg in messages:
        sources[msg.get('log_source', 'unknown')] += 1
    return dict(sources)

def calculate_message_rates(messages):
    msg_times = defaultdict(list)

    for msg in messages:
        if 'timestamp' in msg:
            msg_times[msg.get('msgtype', 'unknown')].append(msg['timestamp'])

    rates = {}
    for msg_type, timestamps in msg_times.items():
        if len(timestamps) > 1:
            duration = max(timestamps) - min(timestamps)
            rates[msg_type] = len(timestamps) / duration if duration > 0 else 0

    return rates

def analyze_errors(messages):
    error_msgs = [msg for msg in messages if
                 any(err in msg.get('msgtype', '').upper()
                     for err in ['ERROR', 'FAIL', 'WARN'])]

    error_types = defaultdict(int)
    for msg in error_msgs:
        error_types[msg.get('msgtype', 'unknown')] += 1

    return {
        'total_errors': len(error_msgs),
        'error_types': dict(error_types)
    }

def save_plot_to_bytes(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight', dpi=300)
    buf.seek(0)
    return buf

def generate_pdf_report(all_analyses, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Collect Elements
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    heading_style = styles['Heading2']
    normal_style = styles['Normal']

    # Title
    elements.append(Paragraph("MAVLink Log Analysis Report", title_style))
    elements.append(Spacer(1, 30))

    # Timestamp
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
    elements.append(Spacer(1, 20))

    # Generate Visualizations
    print("Generating visualizations for PDF...")

    try:
        # 1. Message Count Comparison
        plt.figure(figsize=(15, 6))
        file_names = list(all_analyses.keys())
        message_counts = [analysis['message_distribution']['total_messages']
                         for analysis in all_analyses.values()]

        plt.bar(range(len(file_names)), message_counts, color='skyblue')
        plt.xticks(range(len(file_names)), file_names, rotation=45, ha='right')
        plt.title('Total Messages per Log File')
        plt.ylabel('Number of Messages')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save Plot to Buffer for Adding to PDF
        buf = save_plot_to_bytes(plt.gcf())
        elements.append(Paragraph("Message Distribution", heading_style))
        elements.append(Image(buf, width=7*inch, height=3*inch))
        elements.append(Spacer(1, 20))
        plt.close()

        # Individual File Analysis
        elements.append(Paragraph("Individual File Analysis", heading_style))
        elements.append(Spacer(1, 20))

        for idx, (file_name, analysis) in enumerate(all_analyses.items()):
            # Add file header
            elements.append(Paragraph(f"File: {file_name}", heading_style))
            elements.append(Spacer(1, 10))

            # Message Distribution
            md = analysis['message_distribution']
            elements.append(Paragraph("Message Distribution:", heading_style))
            elements.append(Paragraph(f"Total Messages: {md['total_messages']}", normal_style))
            elements.append(Paragraph(f"Unique Message Types: {md['unique_message_types']}", normal_style))
            elements.append(Spacer(1, 10))

            # Top 10 Message Types Table
            elements.append(Paragraph("Top 10 Message Types:", heading_style))
            sorted_msgs = sorted(md['message_types'].items(),
                               key=lambda x: x[1]['count'],
                               reverse=True)[:10]

            table_data = [['Message Type', 'Count']]
            table_data.extend([[msg_type, str(info['count'])] for msg_type, info in sorted_msgs])

            table = Table(table_data, colWidths=[4*inch, 1*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
            elements.append(Spacer(1, 20))

            # Timing Analysis
            if 'timing_analysis' in analysis and analysis['timing_analysis']:
                ta = analysis['timing_analysis']
                elements.append(Paragraph("Timing Analysis:", heading_style))
                elements.append(Paragraph(f"Duration: {ta['duration_seconds']:.2f} seconds", normal_style))
                elements.append(Paragraph(f"Average Message Rate: {ta['message_rate']:.2f} msgs/sec", normal_style))
                elements.append(Spacer(1, 20))

            # Communication Stats
            cs = analysis['communication_stats']
            elements.append(Paragraph("Communication Statistics:", heading_style))
            for source, count in cs['source_distribution'].items():
                elements.append(Paragraph(f"{source}: {count} messages", normal_style))
            elements.append(Spacer(1, 20))

            # Add Page Breaks Between Files
            if idx < len(all_analyses) - 1:
                elements.append(PageBreak())

        # Build PDF
        print("Building PDF...")
        doc.build(elements)
        print(f"PDF report generated: {output_path}")

    except Exception as e:
        print(f"Error generating PDF report: {e}")
        # Handle Errors Gracefully
        with open(output_path.replace('.pdf', '.txt'), 'w') as f:
            f.write("Error generating PDF report. Generating text report instead.\n\n")
            for file_name, analysis in all_analyses.items():
                f.write(generate_report(analysis))
                f.write("\n" + "="*50 + "\n")

def generate_report(analysis):
    report = []

    # Overview
    report.append("\n=== MAVLink Log Analysis Report ===\n")

    # Message Distribution
    md = analysis['message_distribution']
    report.append("Message Distribution:")
    report.append(f"- Total Messages: {md['total_messages']}")
    report.append(f"- Unique Message Types: {md['unique_message_types']}")
    report.append("\nTop 10 Message Types:")
    sorted_msgs = sorted(md['message_types'].items(),
                        key=lambda x: x[1]['count'],
                        reverse=True)[:10]
    for msg_type, info in sorted_msgs:
        report.append(f"- {msg_type}: {info['count']} messages")

    # Timing Analysis
    if 'timing_analysis' in analysis and analysis['timing_analysis']:
        ta = analysis['timing_analysis']
        report.append("\nTiming Analysis:")
        report.append(f"- Duration: {ta['duration_seconds']:.2f} seconds")
        report.append(f"- Average Message Rate: {ta['message_rate']:.2f} msgs/sec")
        report.append("- Timestamp Gaps:")
        for key, value in ta['timestamp_gaps'].items():
            report.append(f"  - {key}: {value:.4f} seconds")

    # Communication Stats
    cs = analysis['communication_stats']
    report.append("\nCommunication Statistics:")
    report.append("- Source Distribution:")
    for source, count in cs['source_distribution'].items():
        report.append(f"  - {source}: {count} messages")

    # Error Analysis
    ea = analysis['error_analysis']
    report.append("\nError Analysis:")
    report.append(f"- Total Error/Warning Messages: {ea['total_errors']}")
    if ea['error_types']:
        report.append("- Error Types:")
        for error_type, count in ea['error_types'].items():
            report.append(f"  - {error_type}: {count}")

    return "\n".join(report)

def analyze_log_data(data):
    messages = data['messages']
    summary = data['summary']

    analyses = {
        'message_distribution': {},
        'timing_analysis': {},
        'system_status': {},
        'communication_stats': {},
        'error_analysis': {},
        'raw_data': {
            'timestamps': [],
            'message_types': [],
            'sources': []
        }
    }

    # Extract Raw Data for Plotting
    for msg in messages:
        if 'timestamp' in msg:
            analyses['raw_data']['timestamps'].append(msg['timestamp'])
            analyses['raw_data']['message_types'].append(msg.get('msgtype', 'unknown'))
            analyses['raw_data']['sources'].append(msg.get('log_source', 'unknown'))

    # Message Distribution Analysis
    msg_types = defaultdict(lambda: {'count': 0, 'sources': defaultdict(int)})
    for msg in messages:
        msg_type = msg.get('msgtype', 'unknown')
        source = msg.get('log_source', 'unknown')
        msg_types[msg_type]['count'] += 1
        msg_types[msg_type]['sources'][source] += 1

    analyses['message_distribution'] = {
        'message_types': dict(msg_types),
        'total_messages': len(messages),
        'unique_message_types': len(msg_types)
    }

    # Timing Analysis
    timestamps = analyses['raw_data']['timestamps']
    if timestamps:
        analyses['timing_analysis'] = {
            'start_time': min(timestamps),
            'end_time': max(timestamps),
            'duration_seconds': max(timestamps) - min(timestamps),
            'message_rate': len(timestamps) / (max(timestamps) - min(timestamps)),
            'timestamp_gaps': analyze_timestamp_gaps(timestamps)
        }

    # System Status Analysis
    heartbeats = [msg for msg in messages if msg.get('msgtype') == 'HEARTBEAT']
    if heartbeats:
        analyses['system_status'] = analyze_system_status(heartbeats)

    # Communication Statistics
    analyses['communication_stats'] = {
        'source_distribution': analyze_source_distribution(messages),
        'message_rates': calculate_message_rates(messages)
    }

    # Error Analysis
    analyses['error_analysis'] = analyze_errors(messages)

    return analyses

def generate_comparative_visualizations(all_analyses):
    # Matplotlib's Default Style
    plt.style.use('default')

    # Adjust Figure Parameters for Readability
    plt.rcParams.update({
        'figure.autolayout': True,
        'font.size': 10,
        'axes.labelsize': 12,
        'axes.titlesize': 14
    })

    # 1. Message Count Comparison
    plt.figure(figsize=(15, 6))
    file_names = list(all_analyses.keys())
    message_counts = [analysis['message_distribution']['total_messages']
                     for analysis in all_analyses.values()]

    plt.bar(range(len(file_names)), message_counts, color='skyblue')
    plt.xticks(range(len(file_names)), file_names, rotation=45, ha='right')
    plt.title('Total Messages per Log File')
    plt.ylabel('Number of Messages')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 2. Message Type Distribution
    plt.figure(figsize=(15, 6))
    all_message_types = set()
    for analysis in all_analyses.values():
        all_message_types.update(analysis['message_distribution']['message_types'].keys())

    top_types = []
    for msg_type in all_message_types:
        total_count = sum(analysis['message_distribution']['message_types'].get(msg_type, {'count': 0})['count']
                         for analysis in all_analyses.values())
        top_types.append((msg_type, total_count))

    top_types.sort(key=lambda x: x[1], reverse=True)
    top_10_types = top_types[:10]

    plt.bar(range(len(top_10_types)), [t[1] for t in top_10_types], color='lightcoral')
    plt.xticks(range(len(top_10_types)), [t[0] for t in top_10_types], rotation=45, ha='right')
    plt.title('Top 10 Message Types Across All Logs')
    plt.ylabel('Total Message Count')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 3. Source Distribution
    plt.figure(figsize=(15, 6))
    x = range(len(file_names))

    for file_name, analysis in all_analyses.items():
        sources = analysis['communication_stats']['source_distribution']
        tlog_count = sources.get('tlog', 0)
        rlog_count = sources.get('rlog', 0)

        plt.bar(file_names.index(file_name), tlog_count, label='TLOG' if file_name == file_names[0] else "",
                color='lightblue', alpha=0.8)
        plt.bar(file_names.index(file_name), rlog_count, bottom=tlog_count,
                label='RLOG' if file_name == file_names[0] else "", color='lightgreen', alpha=0.8)

    plt.xticks(x, file_names, rotation=45, ha='right')
    plt.title('Message Source Distribution')
    plt.ylabel('Number of Messages')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 4. Duration Comparison
    plt.figure(figsize=(15, 6))
    durations = [analysis['timing_analysis'].get('duration_seconds', 0)
                for analysis in all_analyses.values()]

    plt.bar(range(len(file_names)), durations, color='mediumseagreen')
    plt.xticks(range(len(file_names)), file_names, rotation=45, ha='right')
    plt.title('Log Duration Comparison')
    plt.ylabel('Duration (seconds)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

    # 5. Message Rates
    plt.figure(figsize=(15, 6))
    rates = [analysis['timing_analysis'].get('message_rate', 0)
             for analysis in all_analyses.values()]

    plt.bar(range(len(file_names)), rates, color='mediumpurple')
    plt.xticks(range(len(file_names)), file_names, rotation=45, ha='right')
    plt.title('Message Rate Comparison')
    plt.ylabel('Messages per Second')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()

def analyze_all_logs(directory_path):
    # Retrieve Merged JSON Files
    merged_files = glob.glob(os.path.join(directory_path, '*_merged.json'))

    if not merged_files:
        print(f"No merged log files found in {directory_path}")
        return

    print(f"Found {len(merged_files)} merged log files")

    # Store Analyses
    all_analyses = {}

    # Process File
    for file_path in merged_files:
        file_name = os.path.basename(file_path)
        print(f"\nAnalyzing: {file_name}")

        try:
            # Analyze Data
            with open(file_path, 'r') as f:
                data = json.load(f)

            analysis = analyze_log_data(data)
            all_analyses[file_name] = analysis

            # Generate Individual Reports for Each JSON
            report = generate_report(analysis)
            print(report)

        except Exception as e:
            print(f"Error analyzing {file_name}: {e}")
            continue

    if all_analyses:
        # Comparative Visualizations
        print("\nGenerating comparative visualizations...")
        generate_comparative_visualizations(all_analyses)

        # Generate PDF
        print("\nGenerating PDF report...")
        output_pdf = os.path.join(directory_path, 'mavlink_analysis_report.pdf')
        generate_pdf_report(all_analyses, output_pdf)

    return all_analyses

# Run Analysis
directory_path = '/content/sample_data/merged_logs'
all_analyses = analyze_all_logs(directory_path)
