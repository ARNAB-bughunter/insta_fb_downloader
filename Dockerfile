FROM redhat/ubi9-minimal:9.5-1731604394
 
RUN microdnf install -y \
        python3.11 \
        python3.11-pip \
        python3.11-devel \
        nano
 
RUN mkdir /insta_fb_downloader

WORKDIR /insta_fb_downloader

COPY requirements.txt /insta_fb_downloader
 
RUN pip3.11 install -r requirements.txt --no-deps --default-timeout=200
 
RUN rm -rf /root/.cache \
&& microdnf clean all

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "9191", "--workers", "4"]