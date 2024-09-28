import asyncio
import logging
from go2_webrtc_driver.webrtc_driver import Go2WebRTCConnection, WebRTCConnectionMethod
from aiortc import MediaStreamTrack
from aiortc.contrib.media import MediaRecorder
import cv2
import os
import queue

# Enable logging for debugging
logging.basicConfig(level=logging.FATAL)

imgq = queue.Queue(10)

# This function receives video frames from the camera stream
async def recv_camera_stream(track: MediaStreamTrack):
    global imgq

    while True:
        frame = await track.recv()

        # Convert the video frame to a NumPy array in BGR format (for OpenCV)
        img = frame.to_ndarray(format="bgr24")

        print(f"Shape: {img.shape}, Dimensions: {img.ndim}, Type: {img.dtype}, Size: {img.size}")
        try:
            imgq.put_nowait(img)
        finally:
            pass

    # When the loop ends, close the OpenCV window
    cv2.destroyAllWindows()

# Main function for setting up the WebRTC connection and handling streams
async def main():
    global img

    try:
        # Choose a connection method (uncomment the correct one)
        conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, ip=os.getenv('ROBOT_IP', '192.168.8.181'))
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalSTA, serialNumber="B42D2000XXXXXXXX")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.Remote, serialNumber="B42D2000XXXXXXXX", username="email@gmail.com", password="pass")
        # conn = Go2WebRTCConnection(WebRTCConnectionMethod.LocalAP)

        # Connect to the device
        await conn.connect()

        # Switch video channel on and start receiving video frames
        conn.video.switchVideoChannel(True)

        # Add callback to handle received video frames (track)
        conn.video.add_track_callback(recv_camera_stream)

        while True:
            try:
                img = imgq.get_nowait()

                # Show the frame on the main thread
                cv2.imshow('Camera Stream', img)

                # OpenCV requires a small delay; this also checks for 'q' to quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            except:
                await asyncio.sleep(0.01)

    except ValueError as e:
        logging.error(f"Error in WebRTC connection: {e}")


if __name__ == "__main__":
    asyncio.run(main())
