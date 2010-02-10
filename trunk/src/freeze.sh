#!/bin/sh

DIST=dist

[ -d $DIST ] && rm -r $DIST
cxfreeze mainwin.py --target-dir $DIST
svn export ../data/ $DIST/data
svn export ../pixbufs/ $DIST/pixbufs
while read i
do
    cp $i $DIST
done << EOF
/usr/lib/libpyglib-2.0-python2.6.so.0
/usr/lib/libglitz-glx.so.1
/usr/lib/opengl/xorg-x11/lib/libGL.so.1
/usr/lib/libglitz.so.1
EOF
cat << EOF >$DIST/gmbox
#!/bin/sh
LD_LIBRARY_PATH=. ./mainwin
EOF
chmod +x $DIST/gmbox
tar zcvf gmbox.tar.gz $DIST

#对于没有GTK的环境，可能还需要以下so
#/usr/lib/libgobject-2.0.so.0
#/usr/lib/libgthread-2.0.so.0
#/usr/lib/libglib-2.0.so.0
#/usr/lib/libgtk-x11-2.0.so.0
#/usr/lib/libgdk-x11-2.0.so.0
#/usr/lib/libatk-1.0.so.0
#/usr/lib/libgdk_pixbuf-2.0.so.0
#/usr/lib/libgio-2.0.so.0
#/usr/lib/libpangocairo-1.0.so.0
#/usr/lib/libpangoft2-1.0.so.0
#/usr/lib/libcairo.so.2
#/usr/lib/libpixman-1.so.0
#/usr/lib/libxcb.so.1
#/usr/lib/libpango-1.0.so.0
#/usr/lib/libfontconfig.so.1
#/usr/lib/libexpat.so.1
#/usr/lib/libgmodule-2.0.so.0
#/usr/lib/libXcomposite.so.1
#/usr/lib/libXdamage.so.1
#/usr/lib/libXfixes.so.3
#/usr/lib/libXxf86vm.so.1
#/usr/lib/libdrm.so.2
