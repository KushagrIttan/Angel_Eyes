import cv2
import mediapipe as mp
import time_disp
import time
import math
import numpy as np
import json
import location
    
def alerter():
    mp_hands = mp.solutions.hands
    mp_pose = mp.solutions.pose
    mp_face_mesh = mp.solutions.face_mesh
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.7, min_tracking_confidence=0.7)

    loc=location.device_location()

    log_file = "cd_zn_final/file_log.json"
    log_data = []
    fist_detected = False

    mp_drawing = mp.solutions.drawing_utils

    cap = cv2.VideoCapture(0)

    prev_left_hand_x = None
    prev_right_hand_x = None
    attack_threshold = 0.1
    attack_detected = False
    attack_start_time = 0


    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            continue

        image = cv2.cvtColor(cv2.flip(image, 1), cv2.COLOR_BGR2RGB)
        image.flags.writeable = False
        results_pose = pose.process(image)
        results_hand = hands.process(image)
        results_face = face_mesh.process(image)
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        #angry face detection
        if results_face.multi_face_landmarks:
            for face_landmarks in results_face.multi_face_landmarks:
                # Get landmarks for eyebrows and mouth
                left_eyebrow_upper = [face_landmarks.landmark[i] for i in [65, 66, 67, 68, 69, 70, 107]]
                right_eyebrow_upper = [face_landmarks.landmark[i] for i in [295, 296, 297, 298, 299, 300, 336]]
                mouth_upper = [face_landmarks.landmark[i] for i in [13, 14, 17, 39, 37, 40, 181, 82, 81, 80, 191]]
                mouth_lower = [face_landmarks.landmark[i] for i in [87, 84, 17, 314, 317, 402, 318, 415, 310, 311, 312]]

                # Calculate eyebrow and mouth distances
                left_eyebrow_dist = np.mean([abs(left_eyebrow_upper[0].y - left_eyebrow_upper[-1].y)])
                right_eyebrow_dist = np.mean([abs(right_eyebrow_upper[0].y - right_eyebrow_upper[-1].y)])
                mouth_dist = np.mean([abs(mouth_upper[0].y - mouth_lower[0].y)])

                # Angry detection logic (simplified)
                # if left_eyebrow_dist < 0.01 and right_eyebrow_dist < 0.01 and mouth_dist < 0.015: #Adjust these thresholds
                #     image_width = image.shape[1]
                #     cv2.putText(image, "Angry Face Detected!", (image_width - 1905, 100), cv2.FONT_HERSHEY_SIMPLEX, 1,
                #                 (0, 0, 255), 2)

                # logging the face data
                #     if not fist_detected:
                #         fist_detected = True
                #         timestamp = datetime.datetime.now().isoformat()
                #         log_entry = {"timestamp": timestamp}
                #         log_data.append(log_entry)
                #
                #         print(f"angry face detected , {timestamp} , {loc}")
                #
                #         with open(log_file, "w") as f:
                #             json.dump(log_data, f, indent=4)
                # else:
                #     fist_detected = False  # reset detection flag.

                # face mesh
                # mp_drawing.draw_landmarks(image, face_landmarks, mp_face_mesh.FACEMESH_TESSELATION,
                #                           mp_drawing.DrawingSpec(color=(80, 110, 10), thickness=1, circle_radius=1),
                #                           mp_drawing.DrawingSpec(color=(80, 256, 121), thickness=1, circle_radius=1))


        #fist alert
        if results_hand.multi_hand_landmarks:
            for hand_landmarks in (results_hand.multi_hand_landmarks):
                # Get landmarks for wrist, thumb, and pinky
                wrist = hand_landmarks.landmark[mp_hands.HandLandmark.WRIST]
                thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                pinky_tip = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP]

                # Calculate distance between thumb and pinky
                distance = math.sqrt((thumb_tip.x - pinky_tip.x)**2 + (thumb_tip.y - pinky_tip.y)**2)

                # Calculate distance from wrist to the middle of thumb and pinky.
                middle_x = (thumb_tip.x+pinky_tip.x)/2
                middle_y = (thumb_tip.y+pinky_tip.y)/2
                wrist_dist_middle = math.sqrt((wrist.x - middle_x)**2 + (wrist.y - middle_y)**2)

                # Check if thumb and pinky are close and wrist is relatively close to the middle of the hand.
                if distance < 0.1 and wrist_dist_middle < 0.15: #Adjust these thresholds
                    #cv2.putText(image, "Threat detected!", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    image_width = image.shape[1]  # gets the image width
                    cv2.putText(image, "Threat Detected", (image_width - 1905, 150), cv2.FONT_HERSHEY_SIMPLEX, 1,
                                (0, 0, 255), 2)
                    if not fist_detected:
                        fist_detected = True
                        timestamp = time_disp.show_time_and_date()
                        log_entry = {"category": "threat detected", "timestamp": timestamp, "location": loc}
                        log_data.append(log_entry)
                        print(f"Fist detected , {timestamp} , {loc}")

                        with open(log_file, "w") as f:
                            json.dump(log_data, f, indent=4)
                else:
                    fist_detected = False  # reset detection flag.

                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=5, circle_radius=4),  # Landmark style
                    mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=8),  # Connection style
                )

        # cv2.imshow('Threat detected!', image)

        #attack alert
        if results_pose.pose_landmarks:
            landmarks = results_pose.pose_landmarks.landmark
            left_hand = landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value]
            right_hand = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value]
            nose = landmarks[mp_pose.PoseLandmark.NOSE.value]


            # mp_drawing.draw_landmarks(
            #     image,
            #     results_pose.pose_landmarks,
            #     mp_hands.HAND_CONNECTIONS,
            #     mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=5, circle_radius=4),  # Landmark style
            #     mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=8),  # Connection style
            # )
            mp_drawing.draw_landmarks(
                image, results_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=5, circle_radius=4),  # Landmark style
                mp_drawing.DrawingSpec(color=(255, 0, 0), thickness=8),  # Connection style
            )

            if prev_left_hand_x is not None and prev_right_hand_x is not None:
                left_hand_movement = left_hand.x - prev_left_hand_x
                right_hand_movement = right_hand.x - prev_right_hand_x

                if (left_hand_movement < -attack_threshold and abs(left_hand.y - nose.y) < 0.2) or \
                   (right_hand_movement < -attack_threshold and abs(right_hand.y - nose.y) < 0.2) :
                   # (left_hand_movement < -attack_threshold) or \
                   # (left_hand_movement < -attack_threshold) or \
                   # (abs(left_hand.y - nose.y) < 0.2) or \
                   # (abs(right_hand.y - nose.y) < 0.2):
                    attack_detected = True
                    attack_start_time = time.time()  # Record the attack time

            prev_left_hand_x = left_hand.x
            prev_right_hand_x = right_hand.x

        if attack_detected:
            if time.time() - attack_start_time < 2:  # Display for 2 seconds
                image_width = image.shape[1]  # gets the image width
                cv2.putText(image, "attack Detected", (image_width - 1905, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                        (0, 0, 255), 2)
                if not fist_detected:
                    fist_detected = True
                    timestamp = time_disp.show_time_and_date()
                    log_entry = {"category":"threat detected","timestamp": timestamp,"location":loc}
                    log_data.append(log_entry)

                    print(f"attack alert , {timestamp} , {loc}")

                    with open(log_file, "w") as f:
                        json.dump(log_data, f, indent=4)
            else:
                fist_detected = False  # reset detection flag.
                attack_detected = False  # Reset the flag



        cv2.imshow('Attack Detection', image)
        if cv2.waitKey(5) & 0xFF == 27:
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    alerter()