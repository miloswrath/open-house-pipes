import re

def generate_rows(users):
    """Generate HTML rows for the leaderboard table."""
    rows = []
    for user in users:
        if user['number'] == '1':
            rows.append(f"""
          <tr class="top">
            <td class="number">{user['number']}</td>
            <td class="name">{user['name']}</td>
            <td class="points">
            {user['points']}
            <img
                class="gold-medal"
                src="https://github.com/malunaridev/Challenges-iCodeThis/blob/master/4-leaderboard/assets/gold-medal.png?raw=true"
                alt="gold medal"
              />
            </td>
          </tr>
        """)
        else:
            rows.append(f"""
            <tr>
                <td class="number">{user['number']}</td>
                <td class="name">{user['name']}</td>
                <td class="points">{user['points']}</td>
            </tr>
            """)
    return "\n".join(rows)

def update_html(file_path, users):
    """Update the leaderboard table with new data."""
    with open(file_path, 'r') as file:
        html_content = file.read()
    
    # Generate new rows
    print("Users before generating rows:", users)
    print("Type of users:", type(users))
    print("Type of each entry in users:", [type(user) for user in users])
    
    # Generate HTML rows (this returns a string)
    new_rows = generate_rows(users)
    print("Generated rows:", new_rows)
    print("Type of new_rows:", type(new_rows))
    
    # Use regex to replace the content within the <table>...</table> tags
    updated_html = re.sub(
        r'(<table>.*?</table>)',
        f'<table>{new_rows}</table>',
        html_content,
        flags=re.DOTALL
    )
    
    with open(file_path, 'w') as file:
        file.write(updated_html)
