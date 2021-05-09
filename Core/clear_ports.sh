sudo kill -9 $(sudo lsof -t -i:12345)
sudo kill -9 $(sudo lsof -t -i:12344)
sudo kill -9 $(sudo lsof -t -i:12346)
echo "Ports cleared successfully."