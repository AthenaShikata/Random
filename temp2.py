line = '[youtube] Extracting URL: https://www.youtube.com/watch?v=zkcq22D3aXM'


if line.find('[youtube] Extracting URL: ') != -1:
    link = line[line.rfind('[youtube] Extracting URL: ') +26:]
    print(link)

print(len('[youtube] Extracting URL: '))