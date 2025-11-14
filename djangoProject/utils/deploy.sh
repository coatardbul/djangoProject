cd /usr/local/pythonProject
source myenv/bin/activate
sleep 3
cd /usr/local/pythonProject/djangoProject

##source myenv/bin/activate


PID=`lsof -i:12888 |awk '{print $2}'`

# 停止 应用
if [ -z "$PID" ]
then
    echo "Application $APP_NAME is already stopped."
else
     for i in $PID
    do
        echo "Kill the $1 process [ $i ]"
        kill -9 $i
    done
fi

nohup  python3.8 manage.py runserver 0.0.0.0:12888   &>/dev/null &
