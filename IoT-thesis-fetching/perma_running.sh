time_sleep=86400

while true; do
    ./fetch_remote_tar.sh
    sleep $time_sleep
done
