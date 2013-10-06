#include <iostream>
#include <time.h>

typedef unsigned char uchar;
void encode(uchar *arr, uchar *res);

int main(){
    volatile uchar array[480][64][3] = { 1};
    volatile uchar frame[480*64*3/8];

    clock_t t = clock();

    std::cout << "Encoding..." << std::endl;

    encode((uchar*)array,(uchar*)frame);

    std::cout << "done" << std::endl;

    std::cout << "Time: " << clock()-t << std::endl;
    return 0;
}

void encode(uchar *arr, uchar *res){
    const uchar mask = 0x80;
    const uchar shift = 15;
    uchar resPos = 0;

    for(uchar *ptr=arr; ptr < arr+480*64*3;){
        uchar byte = 0;
        for(uchar i=8;i-->0;){
            byte <<= 1;
            byte |= (*(ptr++) & mask) >> shift;
        }
        res[resPos++];
    }
}
