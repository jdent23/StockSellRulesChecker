docker build -t lwowski-stock-screener .
docker tag lwowski-stock-screener:latest 120595873264.dkr.ecr.us-east-2.amazonaws.com/lwowski-stock-screener:latest
aws ecr get-login-password --region us-east-2 | docker login --username AWS --password-stdin 120595873264.dkr.ecr.us-east-2.amazonaws.com
docker push 120595873264.dkr.ecr.us-east-2.amazonaws.com/lwowski-stock-screener:latest

