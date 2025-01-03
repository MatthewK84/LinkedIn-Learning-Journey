import os
import glob
from pymavlink import mavutil
import json
from datetime import datetime
from collections import defaultdict
import struct

def parse_rlog_binary(file_path):
    messages = []
    try:
        with open(file_path, 'rb') as f:
            msg_count = 0
            while True:
                byte = f.read(1)
                if not byte:
                    break

                if byte[0] in [0xFD, 0xFE]:  # MAVLink Packet Markers
                    try:
                        if byte[0] == 0xFD:  # MAVLink v2
                            length = int.from_bytes(f.read(1), 'little')
                            if length > 280:  # Max MAVLink v2 Packet Size
                                continue

                            incompat_flags = int.from_bytes(f.read(1), 'little')
                            compat_flags = int.from_bytes(f.read(1), 'little')
                            seq = int.from_bytes(f.read(1), 'little')
                            sysid = int.from_bytes(f.read(1), 'little')
                            compid = int.from_bytes(f.read(1), 'little')
                            msgid = int.from_bytes(f.read(3), 'little')
                            payload = f.read(length)
                            checksum = f.read(2)

                            msg_data = {
                                'msgtype': f'MSG_{msgid}',
                                'system_id': sysid,
                                'component_id': compid,
                                'sequence': seq,
                                'payload_length': length,
                                'log_source': 'rlog'
                            }

                            # Extract Timestamp
                            if length >= 8:
                                try:
                                    msg_data['timestamp'] = struct.unpack('<Q', payload[:8])[0]
                                except:
                                    pass

                            messages.append(msg_data)
                            msg_count += 1

                        else:  # MAVLink v1
                            length = int.from_bytes(f.read(1), 'little')
                            if length > 255:
                                continue

                            seq = int.from_bytes(f.read(1), 'little')
                            sysid = int.from_bytes(f.read(1), 'little')
                            compid = int.from_bytes(f.read(1), 'little')
                            msgid = int.from_bytes(f.read(1), 'little')
                            payload = f.read(length)
                            checksum = f.read(2)

                            msg_data = {
                                'msgtype': f'MSG_{msgid}',
                                'system_id': sysid,
                                'component_id': compid,
                                'sequence': seq,
                                'payload_length': length,
                                'log_source': 'rlog'
                            }

                            if length >= 8:
                                try:
                                    msg_data['timestamp'] = struct.unpack('<Q', payload[:8])[0]
                                except:
                                    pass

                            messages.append(msg_data)
                            msg_count += 1

                        if msg_count % 1000 == 0:
                            print(f"Processed {msg_count} Messages From rlog...", end='\r')

                    except Exception as e:
                        continue

        print(f"\nCompleted Processing rlog: {msg_count} Valid Messages")
        return messages

    except Exception as e:
        print(f"\nError Processing rlog File: {e}")
        return messages

def process_tlog_file(file_path):
    messages = []
    try:
        mlog = mavutil.mavlink_connection(file_path)
        msg_count = 0

        while True:
            try:
                msg = mlog.recv_match(blocking=False)
                if msg is None:
                    break

                if msg.get_type() == 'BAD_DATA':
                    continue

                msg_data = {
                    'msgtype': msg.get_type(),
                    'log_source': 'tlog'
                }

                # Message Fields Addition
                if hasattr(msg, '_fieldnames'):
                    for field in msg._fieldnames:
                        try:
                            value = getattr(msg, field)
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='replace')
                                except:
                                    value = ''.join(format(b, '02x') for b in value)
                            msg_data[field] = value
                        except:
                            continue

                if hasattr(msg, '_timestamp'):
                    msg_data['timestamp'] = msg._timestamp

                messages.append(msg_data)
                msg_count += 1

                if msg_count % 1000 == 0:
                    print(f"Processed {msg_count} Messages From tlog...", end='\r')

            except Exception as e:
                continue

        print(f"\nCompleted Processing tlog: {msg_count} Valid Messages")
        return messages

    except Exception as e:
        print(f"\nError Processing tlog File: {e}")
        return messages

def merge_log_files(directory_path):
    print(f"\nChecking Directory: {directory_path}")

    if not os.path.exists(directory_path):
        print(f"Directory Does Not Exist: {directory_path}")
        return

    # Create Output Directory and Verify it's Writable
    output_dir = os.path.join(directory_path, 'merged_logs')
    try:
        os.makedirs(output_dir, exist_ok=True)
        if not os.access(output_dir, os.W_OK):
            print(f"Error: Output Directory {output_dir} is Not Writable")
            return
        print(f"Output Directory Created and Writable: {output_dir}")
    except Exception as e:
        print(f"Error Creating Output Directory: {str(e)}")
        return

    successful_merges = 0
    partial_merges = []
    failed_merges = []

    # Find All Log Files
    tlog_files = glob.glob(os.path.join(directory_path, '*.tlog'))
    rlog_files = glob.glob(os.path.join(directory_path, '*.rlog'))

    print(f"\nFound {len(tlog_files)} .tlog Files and {len(rlog_files)} .rlog Files")

    if len(tlog_files) == 0 and len(rlog_files) == 0:
        print("No Log Files Found")
        return

    for tlog_file in tlog_files:
        base_name = os.path.splitext(tlog_file)[0]
        rlog_file = base_name + '.rlog'

        if not os.path.exists(rlog_file):
            print(f"\nNo Matching .rlog File Found For {os.path.basename(tlog_file)}")
            failed_merges.append(os.path.basename(tlog_file))
            continue

        print(f"\nProcessing Pair: {os.path.basename(tlog_file)}")
        print(f"TLOG Size: {os.path.getsize(tlog_file)} Bytes")
        print(f"RLOG Size: {os.path.getsize(rlog_file)} Bytes")

        try:
            # Process Files
            tlog_messages = process_tlog_file(tlog_file)
            rlog_messages = parse_rlog_binary(rlog_file)

            print(f"Found {len(tlog_messages)} TLOG Messages and {len(rlog_messages)} RLOG Messages")

            if not tlog_messages and not rlog_messages:
                print("No Valid Messages Found in Either File")
                failed_merges.append(os.path.basename(tlog_file))
                continue
            elif not tlog_messages or not rlog_messages:
                print("Messages Found in Only One File")
                partial_merges.append(os.path.basename(tlog_file))

            # Combine and Sort Messages
            merged_messages = tlog_messages + rlog_messages
            print(f"Combined Into {len(merged_messages)} Total Messages")

            try:
                merged_messages.sort(key=lambda x: x.get('timestamp', 0))
                print("Successfully Sorted Messages by Timestamp")
            except Exception as e:
                print(f"Warning: Could Not Sort Messages by Timestamp: {str(e)}")

            # Summary of Messages
            summary = {
                'total_messages': len(merged_messages),
                'tlog_messages': len(tlog_messages),
                'rlog_messages': len(rlog_messages),
                'message_types': defaultdict(lambda: {'tlog': 0, 'rlog': 0})
            }

            for msg in merged_messages:
                msg_type = msg.get('msgtype', 'unknown')
                source = msg.get('log_source', 'unknown')
                summary['message_types'][msg_type][source] += 1

            summary['message_types'] = dict(summary['message_types'])

            # Merged Data Saved as JSON
            output_file = os.path.join(output_dir, f"{os.path.basename(base_name)}_merged.json")
            print(f"Saving Merged Data To: {output_file}")

            output_data = {
                'summary': summary,
                'messages': [
                    {k: v for k, v in msg.items() if isinstance(v, (str, int, float, bool, type(None)))}
                    for msg in merged_messages
                ]
            }

            try:
                with open(output_file, 'w') as f:
                    json.dump(output_data, f, indent=2, default=str)
                print(f"Successfully Saved Merged File")
                successful_merges += 1
            except Exception as e:
                print(f"Error Saving Merged File: {str(e)}")
                failed_merges.append(os.path.basename(tlog_file))

        except Exception as e:
            print(f"Error Processing Files: {str(e)}")
            failed_merges.append(os.path.basename(tlog_file))

    print("\nMerge Process Complete:")
    print(f"Fully Successful Merges: {successful_merges} File Pairs")
    print(f"Partial Merges: {len(partial_merges)} File Pairs")
    print(f"Failed Merges: {len(failed_merges)} File Pairs")

    if partial_merges:
        print("\nPartial Merge Files:")
        for file in partial_merges:
            print(f"- {file}")

    if failed_merges:
        print("\nFailed Files:")
        for file in failed_merges:
            print(f"- {file}")

    print(f"\nMerged Files Can Be Found In: {output_dir}")

# Directory Path
directory_path = '/content/sample_data'

# Process and Merge Files
print("Starting Log File Merge Process...")
merge_log_files(directory_path)
