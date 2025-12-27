#ifndef __GLIBC_MACROS_H__
#define __GLIBC_MACROS_H__

#define __GNUC_PREREQ(maj, min) (((__GNUC__ << 16) + __GNUC_MINOR__) >= (((maj) << 16) + (min)))
#define __glibc_clang_prereq(maj, min) 0

#endif