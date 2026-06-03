def check_tags(file_path):
    with open(file_path) as f:
        html = f.read()
    
    # Just a simple count of <div and </div
    opens = html.count('<div')
    closes = html.count('</div')
    print(f"{file_path}: {opens} opens, {closes} closes")

check_tags('templates/users_add.html')
check_tags('templates/roles_add.html')
