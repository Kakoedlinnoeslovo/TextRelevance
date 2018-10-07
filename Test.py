print(",".join(str(pos) for pos in [1, 2, 3]))

from collections import defaultdict
from inscriptis import get_text

d = defaultdict(list)
print(d['te'])

html = '''
       <html>
       111111
       <body>
       2222222
       <div> 333333 </div>
       <span> 4444 </span>
       <span> <b>Производитель</b> </span> <span> ASUS </span> </li> 
       </body>
       ddddd
       </html>
       rrrrr
       '''

print(get_text(html))


#from inscriptis import get_text
#import re
#import subprocess
#import os
#print(os.path.exists("example.txt"))


#test_str = "124 fffs     ffff           sdfsdff"
#print(get_text(test_str))

#print(('   '.strip(), 'ddd'))

#print(test_str)
#print(re.sub(r'\W+', ' ', test_str))

#s='abcd2343 abw34324 abc3243-23A'
#print(re.split('(\d+)',s))

#print(re.search(r'<title>(.*?)<\/title>', '<title>kkk777 sd</title> 12 abc 44 d d').groups()[0])
#print(get_text('<title>kkk777 sd</title> 12 abc 44 d d'))

#out = ''
#subprocess.call(["mystem.exe", "-ldc", "example.txt", "out1.txt"])
#print(out)

#print(hash("fdsdfsdfsdf"))

#f = open("example.txt", 'r', encoding='utf-8')
#print("1) ", f.readline())
#print("2) ", f.read())
#f.close()
