# kzip cracker
**Supports AES encrypted zip files.**  
This tool bruteforce enumerates over all possible passwords discovering matching
 password for given file.  
Huge performance improvement was archived with multiprocessing lib, by default application is
 spawns exactly 10 jobs that independently crack 100 passwords each.

#### TESTED UNDER PYTHON 3.11

## Install requirements
```
pip install -r requirements.txt
```

## Usage:

```shell
python3 zz.py -f test.zip -l 8                    # crack pass with 8 chars at most
python3 zz.py -f test.zip -l 8 -m 200             # each job checks 200 passwords
python3 zz.py -f test.zip -l 8 -p 20              # spawn 20 processes/jobs
python3 zz.py -f test.zip -l 8 -c 22611800        # continue from previous last index
python3 zz.py -f test.zip -l 8 -m 200 -c 365700   # continue from previous last index - make sure to set (-m) the same otherwise continue_index with point to different word set
```

### Results
Program prints results as is.  
Not printable or control characters may be hard to read so you are also provided hex representation of that string.

i.e. 
```shell
Tries: 22971800 > l
g [6C:0A:67:0C]
```
Restive results with
```python
string = '6C:0A:67:0C'
print([chr(int(h, 16)) for h in string.split(':')])
>>> ['l', '\n', 'g', '\x0c']
```
Also consult with ASCII table.

