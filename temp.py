import xml.etree.cElementTree as ET
from datetime import datetime

datetime.today().strftime('%Y-%m-%d %H:%M:%S')

episodenfo = ET.Element('episodedetails')
ET.SubElement(episodenfo,'plot').text = (f'{author}\n{channel}\n\nhttps://www.youtube.com/watch?v={videoID}\n\n{description}').rstrip('\n').rstrip(' ')
ET.SubElement(episodenfo,'outline').text = (f'{author}\n{channel}\n\nhttps://www.youtube.com/watch?v={videoID}\n\n{description}').rstrip('\n').rstrip(' ')
ET.SubElement(episodenfo,'lockdata').text = f'false'  
ET.SubElement(episodenfo,'dateadded').text = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
ET.SubElement(episodenfo,'title').text = f'{cleanTitle}'
ET.SubElement(episodenfo,'director').text = f'{author}'
ET.SubElement(episodenfo,'year').text = f'{year}'
ET.SubElement(episodenfo,'genre').text = f'youtube'
ET.SubElement(episodenfo,'tag').text = f'youtube'
art = ET.SubElement(episodenfo, 'art')
ET.SubElement(art,'poster').text = f'/media/youtube/{showtitle} ({showfirstyear})//Season {season}/{titleSE}-thumb.jpg'
actor = ET.SubElement(episodenfo,'actor')
ET.SubElement(actor,'name').text = f'{author}'
ET.SubElement(actor,'type').text = f'Actor'
ET.SubElement(episodenfo,'showtitle').text = f'{showtitle}'
ET.SubElement(episodenfo,'episode').text = f'{episode}'
ET.SubElement(episodenfo,'season').text = f'{season}'
ET.SubElement(episodenfo,'aired').text = f'{date}'

tree = ET.ElementTree(episodenfo)
ET.indent(tree, space="  ", level=0)
out = open("seasonnfo.nfo", 'wb')
out.write(b'<?xml version="1.0" encoding="UTF-8" standalone = "yes"?>\n')
tree.write(out, encoding = 'UTF-8', xml_declaration = False)
out.close()

tvshow = ET.Element('tvshow')
ET.SubElement(tvshow,'enddate').text = f'{lastdate}'
ET.SubElement(tvshow,'genre').text = f'youtube'
ET.SubElement(tvshow,'tag').text = f'youtube'
actor = ET.SubElement(tvshow,'actor')
ET.SubElement(actor,'name').text = f'{author}'
ET.SubElement(actor,'type').text = f'Actor'
ET.SubElement(tvshow,'season').text = f'-1'
ET.SubElement(tvshow,'episode').text = f'-1'
ET.SubElement(tvshow,'status').text = f'Ended'

tree = ET.ElementTree(tvshow)
ET.indent(tree, space="  ", level=0)
out = open("tvshow.nfo", 'wb')
out.write(b'<?xml version="1.0" encoding="UTF-8" standalone = "yes"?>\n')
tree.write(out, encoding = 'UTF-8', xml_declaration = False)
out.close()


''' episodeNFO = f'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n\
  <episodedetails>\n\
    <plot>{author}\n{channel}\n\nhttps://www.youtube.com/watch?v={videoID}\n\n{description}</plot>\n\
    <lockdata>false</lockdata>\n\
    <dateadded>2025-02-20 00:00:00</dateadded>\n\
    <title>{cleanTitle}</title>\n\
    <director>{author}</director>\n\
    <year>{year}</year>\n\
    <genre>youtube</youtube>\n\
    <art>\n\
      <poster>/media/youtube/{showtitle} ({firstyear})/Season {season}/{titleSE}-thumb.jpg</poster>\n\
    </art>\n\
    <actor>\n\
      <name>{author}</name>\n\
      <type>Actor</type>\n\
    </actor>\n\
    <showtitle>{showtitle}</showtitle>\n\
    <episode>{episode}</episode>\n\
    <season>{season}</season>\n\
    <aired>{date}</aired>\n\
  </episodedetails>
'''
'''
    seasonnfo = f'<?xml version="1.0" encoding="utf-8" standalone="yes"?>\n\
    <season>\n\
      <plot>{author}\n{channel}\n{playlist}\n\n{description}</plot>\n\
      <outline>{author}\n{channel}\n{description}</outline>\n\
      <lockdata>false</lockdata>\n\
      <dateadded>2025-02-20 00:00:00</dateadded>\n\
      <title>Season {season}</title>\n\
      <year>{firstyear}</year>\n\
      <premiered>{firstdate}</premiered>\n\
      <releasedate>{firstdate}</releasedate>\n\
      <art>\n\
        <poster>/media/youtube/{showtitle} ({showfirstyear})/season{str(season).zfill(2)}-poster.jpg</poster>\n\
      </art>\n\
      <actor>\n\
        <name>{author}</name>\n\
        <type>Actor</type>\n\
      </actor>\n\
      <seasonnumber>{season}</seasonnumber>'

    seasonNFOfile = open(f'Season {season}/season.nfo','w')
    seasonNFOfile.write(seasonnfo)
    seasonNFOfile.close()'''