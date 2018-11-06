# PartyPi
Simple photo upload webapp that stores photos. Plus script to run fullscreen photoshow of these photos. Best used with a Raspberry Pi and a big screen on a party :)

## Install
At first, install python requirements:
```bash
pip3 install --no-cache-dir -r requirements.txt
```

Then, install node dependencies:
```bash
npm install
```

Create compiled js file:
```bash
npm start
```

## Run it
```bash
python3 ./src/py/partypi.py
```

## Using docker
Build dev image:
```bash
build_dev_image.sh
```

Run dev container:
```bash
run_dev_container.sh
```
