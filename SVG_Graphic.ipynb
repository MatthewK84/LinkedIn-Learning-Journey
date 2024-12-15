import svgwrite

def create_architecture_evaluation():
    # Drawing Initialization
    dwg = svgwrite.Drawing('architecture_evaluation.svg', size=('900px', '600px'))
    
    # Background
    dwg.add(dwg.rect(insert=(0, 0), size=('900px', '600px'), fill='#f8f9fa'))
    
    # Add Title
    title = dwg.text('Systems Architecture Evaluation', 
                     insert=(450, 40),
                     text_anchor='middle',
                     font_family='Arial',
                     font_size=24,
                     fill='#333')
    dwg.add(title)
    
    # Fuzzy Decision Equation Box
    equation_group = dwg.g(transform='translate(50,70)')
    equation_group.add(dwg.rect(insert=(0, 0), 
                              size=('800px', '60px'),
                              fill='white',
                              stroke='#ddd',
                              rx=4))
    equation_group.add(dwg.text('Fuzzy Decision Formula:',
                              insert=(10, 25),
                              font_family='Arial',
                              font_size=14))
    equation_group.add(dwg.text('D = Min(μₚₑᵣf(x), μcost(x), μᵣₑₗ(x), μscal(x), μmaint(x)) where μ represents membership function',
                              insert=(10, 45),
                              font_family='Arial',
                              font_size=14))
    dwg.add(equation_group)

    def create_architecture_card(x_pos, title, score, metrics):
        # Card Group Creation
        card = dwg.g(transform=f'translate({x_pos},150)')
        
        # Card Background Addition
        card.add(dwg.rect(insert=(0, 0),
                         size=('250px', '400px'),
                         fill='white',
                         stroke='#ddd',
                         rx=8))
        
        # Title and Score Addition
        card.add(dwg.text(title,
                         insert=(125, 30),
                         text_anchor='middle',
                         font_family='Arial',
                         font_weight='bold',
                         font_size=16))
        card.add(dwg.text(f'Score: {score}',
                         insert=(125, 50),
                         text_anchor='middle',
                         font_family='Arial',
                         font_size=14))
        
        # Metrics (Simulated)
        metrics_group = dwg.g(transform='translate(20,70)')
        for i, (name, raw_value, mu_value) in enumerate(metrics):
            y_pos = i * 40
            # Metric Names
            metrics_group.add(dwg.text(name,
                                     insert=(0, y_pos + 20)))
            # Metric Values
            metrics_group.add(dwg.text(f'(Raw: {raw_value}, μ: {mu_value})',
                                     insert=(210, y_pos + 20),
                                     text_anchor='end',
                                     font_size=12))
            # Background Bar
            metrics_group.add(dwg.rect(insert=(0, y_pos + 25),
                                     size=('210px', '10px'),
                                     fill='#eee',
                                     rx=5))
            # Add value bar
            width = float(mu_value) * 210
            metrics_group.add(dwg.rect(insert=(0, y_pos + 25),
                                     size=(f'{width}px', '10px'),
                                     fill='#3b82f6',
                                     rx=5))
        card.add(metrics_group)
        
        # Membership Function
        membership = dwg.g(transform='translate(20,300)')
        membership.add(dwg.text('Membership Function:',
                              insert=(0, 20),
                              font_size=12))
        mu_values = [m[2] for m in metrics]
        membership.add(dwg.text(f'μ(x) = Min({", ".join(mu_values)})',
                              insert=(0, 40),
                              font_size=12))
        membership.add(dwg.text(f'μ(x) = {min(float(m) for m in mu_values)}',
                              insert=(0, 60),
                              font_size=12))
        card.add(membership)
        
        return card

    # Architecture Metrics
    monolithic_metrics = [
        ('Performance', '85ms', '0.7'),
        ('Cost', '$150K', '0.4'),
        ('Reliability', '99.9%', '0.9'),
        ('Scalability', '70%', '0.5'),
        ('Maintainability', '65%', '0.4')
    ]

    microservices_metrics = [
        ('Performance', '75ms', '0.6'),
        ('Cost', '$250K', '0.3'),
        ('Reliability', '99.5%', '0.8'),
        ('Scalability', '95%', '0.9'),
        ('Maintainability', '90%', '0.8')
    ]

    hybrid_metrics = [
        ('Performance', '80ms', '0.65'),
        ('Cost', '$200K', '0.35'),
        ('Reliability', '99.7%', '0.85'),
        ('Scalability', '85%', '0.7'),
        ('Maintainability', '80%', '0.6')
    ]

    # Architecture Cards
    dwg.add(create_architecture_card(50, 'Monolithic', '0.400', monolithic_metrics))
    dwg.add(create_architecture_card(325, 'Microservices', '0.300', microservices_metrics))
    dwg.add(create_architecture_card(600, 'Hybrid', '0.350', hybrid_metrics))

    # Legend
    legend = dwg.g(transform='translate(50,570)')
    legend.add(dwg.text('μ = membership function value (0 to 1)',
                       font_size=12))
    legend.add(dwg.text('Raw = actual measured value',
                       insert=(300, 0),
                       font_size=12))
    dwg.add(legend)

    return dwg

if __name__ == '__main__':
    drawing = create_architecture_evaluation()
    drawing.save()
