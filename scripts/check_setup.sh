#!/bin/bash

# Check for Python
if ! command -v python3 &> /dev/null; then
  echo "[ERROR] Python3 is not installed. Please install Python 3.11 or higher."
  echo "Visit: https://www.python.org/downloads/"
  exit 1
fi

# Check for pip
if ! command -v pip3 &> /dev/null; then
  echo "[ERROR] pip3 is not installed. Please install pip for Python 3."
  echo "Try: python3 -m ensurepip --upgrade"
  exit 1
fi

# Check for uv
if ! command -v uv &> /dev/null; then
  echo "[ERROR] uv is not installed."
  read -p "Would you like to install uv with pip3? [y/n] " answer
  if [[ $answer == [Yy] ]]; then
    pip3 install uv
    if ! command -v uv &> /dev/null; then
      echo "[ERROR] uv installation failed. Please install manually: pip3 install uv"
      exit 1
    fi
  else
    echo "Please install uv and rerun the script."
    exit 1
  fi
fi

# Check for poetry
if ! command -v poetry &> /dev/null; then
  echo "[ERROR] poetry is not installed."
  read -p "Would you like to install poetry with pip3? [y/n] " answer
  if [[ $answer == [Yy] ]]; then
    pip3 install poetry
    if ! command -v poetry &> /dev/null; then
      echo "[ERROR] poetry installation failed. Please install manually: pip3 install poetry"
      exit 1
    fi
  else
    echo "Please install poetry and rerun the script."
    exit 1
  fi
fi

# Check for make
if ! command -v make &> /dev/null; then
  echo "[ERROR] make is not installed. Please install make using your system package manager."
  echo "On macOS: brew install make | On Ubuntu: sudo apt-get install make"
  exit 1
fi

# Check for docker
if ! command -v docker &> /dev/null; then
  echo "[ERROR] Docker is not installed. Please install Docker from https://www.docker.com/get-started"
  exit 1
fi

# Check for docker-compose
if ! command -v docker-compose &> /dev/null; then
  echo "[ERROR] docker-compose is not installed."
  echo "On macOS: brew install docker-compose | On Ubuntu: sudo apt-get install docker-compose"
  exit 1
fi

echo "[OK] Python, pip, uv, poetry, make, docker, and docker-compose are installed." 