FROM python:3.11

LABEL name="AiNewsRobot-backed"
LABEL version="0.1.0"
LABEL description="Get a daily summary of ai information"

WORKDIR /app

ADD . ./

# CMD ["python"]