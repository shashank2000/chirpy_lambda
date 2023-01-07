# bluejay

A bluejay is a blue cardinal \[citation needed\].

Despite being blue, it can also be chirpy and chatty.

## Setup instructions

One-time:

`mkdir /tmp/logs`

Every time:

- Run `portforward.sh` as usual.
- `cd bluejay`
- `python3 server.py`

## Notes

Bluejay is not very stable at the moment---it relies on a pipe into another Python process running Chirpy.
Improving this is actively in progress.

## Development Instructions

Bluejay is written in React and Flask.
To develop, run `npm install` as usual. The server will start on `localhost:3000`.
You'll also have to run the main bluejay server as well.

