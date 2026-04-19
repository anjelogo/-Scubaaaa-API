# Scubaaaa API
A hackathon project. Read more about it below:
[The Devpost](https://devpost.com/submit-to/26944-fullyhacks-2026/manage/submissions/998667-scubaaaa/project_details/edit)

## Inspiration
We wanted to build something real; not a web app, not a wrapper, not a simulation. The ocean theme gave us an excuse to put hardware on water and call it a hack. The original vision was a full submarine. We lost a teammate. We shipped anyway.

## What it does
SCUBAAAA is a browser-based mission control for a real remote-operated surface vessel. You open a webpage, get a live camera feed from the vessel, and drive it with a gamepad or keyboard. Real motors. Real wake. Real latency numbers.

## How we built it
The vessel runs on a 2WD chassis controlled by an Arduino UNO over USB serial. A NanoPi R5C onboard handles the camera stream via mediamtx and runs a FastAPI backend over LAN. The frontend is React + Vite + Tailwind, a ocean-themed mission control dashboard with live WebRTC video, gamepad support via the browser Gamepad API, and real-time telemetry over WebSockets. Computer vision runs client-side via TensorFlow.js all locally with no extra server, no added latency.

## Challenges we ran into
The NanoPi R5C has no GPIO, which killed our original motor control plan hours in. We rerouted through an Arduino UNO over USB serial. RTSP doesn't play natively in browsers. Every layer had at least one surprise. We debugged all of them.

## Accomplishments that we're proud of
Getting from zero to a fully operational browser-controlled vessel in 24 hours with a team of three. The hardware arrived mid-competition. We assembled it, flashed firmware, stood up a backend, and had motors responding to gamepad input before most teams had a working frontend.

## What we learned
Hardware is just software with consequences. Serial communication, WebRTC streaming, GPIO constraints, browser CV, where none of us had done all of this before. We learned that the fastest path through a hardware problem is usually one more abstraction layer and a USB cable.

## What's next for Scubaaaa
Actual waterproofing. Depth sensors for real telemetry. A proper CV pipeline for obstacle detection and autonomous navigation. And maybe, finally, the submarine.
