# Triprecco

[![Screenshot-2024-07-26-at-11-27-00-PM.png](https://i.postimg.cc/WzGrxPT0/Screenshot-2024-07-26-at-11-27-00-PM.png)](https://postimg.cc/SYKJz3XK)

## Table of Contents

- [What is Triprecco?](#what-is-triprecco)
- [Hardware Requirements](#hardware-requirements)
- [Software Requirements](#software-requirements)
- [Accessing the App](#accessing-the-app)
- [Contributors](#contributors)

## What is Triprecco?

Do you love to travel but find planning trips a bit overwhelming with all the details like costs, duration, destinations, and activities? We get it! That’s why we created Triprecco, a web app just for you. It uses content-based filtering and similarity search algorithms to find and recommend personalized trip itineraries, making your trip planning faster and easier.

## Hardware Requirements

- Modern Operating System
    - Windows 7 or 10 or above.
    - OS X / MacOS 10.11 or higher.
    - Linux: RHEL 6/7, 64-bit (almost all libraries also work in Ubuntu) or above.
- x86 64-bit CPU (Intel/AMD architecture) or arm64 (MacOS)
- 4GB RAM or above.
- 5GB free disk space or above.

## Software Requirements

- Python 3.12 (This version is necessary as the TF-IDF vectorizer was fitted using this version of Python)
- Any web browser, preferably Google Chrome or Mozilla Firefox.
- Code Editor: VSCode

## Accessing the App

1. To start using Triprecco, clone this GitHub repository.
2. In the root directory of the folder, run the following command in your shell/terminal to install the necessary packages:

    ```
    pip install -r requirements.txt
    ```
3. Afterwards, in the root directory, you can start the app by running the following command:

    ```
    streamlit run app.py
    ```

4. At this point, the application should start and you will be redirected to the browser. Happy planning!

    [![triprecco-fyp.png](https://i.postimg.cc/6q3MC0Zk/triprecco-fyp.png)](https://postimg.cc/R6k1BwXd)

5. Alternatively, should you encounter any issues with running the application in your environment, you can access the deployed application [here](https://triprecco.streamlit.app/).

## Contributors

- Farhan
- Tze Kit
- Rachel
- Xavier
- Rayner
