rm -f _encoder.c
echo === Python 2 ===
echo
python2 setup.py build_ext -i
echo
echo === Python 3 ===
echo
python3 setup.py build_ext -i
