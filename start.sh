if [ -z $SOURCE_CODE ]
then
  echo "Cloning main Repository"
  git clone https://github.com/Kousthubhbhat/WEB-Content-Notify-V2.git /WEB-Content-Notify-V2
else
  echo "Cloning Custom Repo from $SOURCE_CODE "
  git clone $SOURCE_CODE /WEB-Content-Notify-V2
fi
cd /WEB-Content-Notify-V2
pip3 install -U -r requirements.txt
echo "Starting Bot...."
python3 -m main