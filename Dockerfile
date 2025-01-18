# Usa un'immagine base di Python
FROM python:3.12-slim

# Installa le dipendenze base per usare il container in debug
RUN apt-get update && apt-get install -y \
  git \
  zsh \
  tmux \
  vim \
  silversearcher-ag \
  exuberant-ctags \
  fonts-powerline
  
# Clona il repository dotfiles e installa
RUN git clone https://github.com/giursino/dotfiles.git /root/dotfiles && \
  cd /root/dotfiles && \
  ./install

# Installa le dipendenze necessarie per il progetto
RUN apt install -y  \
  python3-tk \
  wget \
  gnupg

# Installa Firefox e geckodriver
RUN apt-get install -y firefox-esr \
  && wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz \
  && tar -xzf geckodriver-v0.30.0-linux64.tar.gz \
  && mv geckodriver /usr/local/bin/ \
  && rm geckodriver-v0.30.0-linux64.tar.gz

# Pulisce la cache dei pacchetti
RUN apt-get clean

# Imposta la directory di lavoro nel container
WORKDIR /app

# Copia il file requirements.txt nella directory di lavoro
COPY requirements.txt .

# Installa le dipendenze specificate in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copia il resto del codice dell'applicazione nella directory di lavoro
COPY . .

# Comando di default per eseguire l'applicazione
CMD ["python", "main.py"]
