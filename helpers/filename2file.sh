date: 1.sh
#!/bin/bash
path=`pwd`
cd $path
for filename in `ls`
do
	date=`echo date: $filename|cut -c1-16`
	echo $date
	sed -i "1i$date" $filename
done
