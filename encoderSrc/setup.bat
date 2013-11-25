@echo off
echo === Python 2 ===

echo .
python setup.py build_ext -i

echo .
echo === Python 3 ===

echo .
python3 setup.py build_ext -i

echo .
pause
