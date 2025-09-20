
import cv2
import mediapipe as mp
import numpy as np
import tempfile
from typing import Dict, Any
import os

class AIProcessor:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def process_video(self, video_path: str, test_type: str) -> Dict[str, Any]:
        """
        Process exercise video and return analysis results
        """
        cap = cv2.VideoCapture(video_path)
        results = {
            "frames_processed": 0,
            "landmarks": [],
            "metrics": {},
            "feedback": [],
            "cheat_detected": False
        }
        
        frame_count = 0
        while cap.isOpened():
            success, image = cap.read()
            if not success:
                break
                
            # Process frame with MediaPipe
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pose_results = self.pose.process(image_rgb)
            
            if pose_results.pose_landmarks:
                results["landmarks"].append(self._extract_keypoints(pose_results.pose_landmarks))
                
                # Test-specific analysis
                if test_type == "pushups":
                    self._analyze_pushup(image, pose_results.pose_landmarks, results, frame_count)
                
            frame_count += 1
            
        cap.release()
        
        # Calculate final metrics
        results["frames_processed"] = frame_count
        self._calculate_final_metrics(results, test_type)
        
        return results
    
    def _extract_keypoints(self, landmarks):
        """Extract key pose landmarks"""
        keypoints = {}
        for idx, landmark in enumerate(landmarks.landmark):
            if idx in [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]:  # Key joints
                keypoints[idx] = {
                    "x": landmark.x,
                    "y": landmark.y,
                    "z": landmark.z,
                    "visibility": landmark.visibility
                }
        return keypoints
    
    def _analyze_pushup(self, image, landmarks, results, frame_count):
        """Analyze pushup form and count repetitions"""
        # Extract key joints
        left_shoulder = landmarks.landmark[11]
        right_shoulder = landmarks.landmark[12]
        left_elbow = landmarks.landmark[13]
        right_elbow = landmarks.landmark[14]
        left_wrist = landmarks.landmark[15]
        right_wrist = landmarks.landmark[16]
        
        # Calculate elbow angles
        left_angle = self._calculate_angle(left_shoulder, left_elbow, left_wrist)
        right_angle = self._calculate_angle(right_shoulder, right_elbow, right_wrist)
        avg_angle = (left_angle + right_angle) / 2
        
        # Track angles for repetition counting
        if "elbow_angles" not in results["metrics"]:
            results["metrics"]["elbow_angles"] = []
        results["metrics"]["elbow_angles"].append(avg_angle)
        
        # Detect repetition phases
        self._detect_pushup_phases(results, avg_angle, frame_count)
        
        # Check form (back straightness, elbow position, etc.)
        self._check_pushup_form(landmarks, results)
    
    def _calculate_angle(self, a, b, c):
        """Calculate angle between three points"""
        a = np.array([a.x, a.y])
        b = np.array([b.x, b.y])
        c = np.array([c.x, c.y])
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        
        if angle > 180.0:
            angle = 360 - angle
            
        return angle
    
    def _detect_pushup_phases(self, results, angle, frame_count):
        """Detect pushup phases and count repetitions"""
        if "phases" not in results["metrics"]:
            results["metrics"]["phases"] = []
            results["metrics"]["repetitions"] = 0
            results["metrics"]["current_phase"] = "top"  # Start at top position
        
        # Phase detection logic
        if results["metrics"]["current_phase"] == "top" and angle > 160:
            results["metrics"]["current_phase"] = "descending"
        elif results["metrics"]["current_phase"] == "descending" and angle < 90:
            results["metrics"]["current_phase"] = "bottom"
        elif results["metrics"]["current_phase"] == "bottom" and angle > 90:
            results["metrics"]["current_phase"] = "ascending"
        elif results["metrics"]["current_phase"] == "ascending" and angle > 160:
            results["metrics"]["current_phase"] = "top"
            results["metrics"]["repetitions"] += 1
            
        results["metrics"]["phases"].append({
            "frame": frame_count,
            "phase": results["metrics"]["current_phase"],
            "angle": angle
        })
    
    def _check_pushup_form(self, landmarks, results):
        """Check for proper pushup form and detect cheating"""
        # Check back straightness (hip and shoulder alignment)
        left_shoulder = landmarks.landmark[11]
        right_shoulder = landmarks.landmark[12]
        left_hip = landmarks.landmark[23]
        right_hip = landmarks.landmark[24]
        
        shoulder_avg_y = (left_shoulder.y + right_shoulder.y) / 2
        hip_avg_y = (left_hip.y + right_hip.y) / 2
        
        # If hips are significantly lower than shoulders, back might be arched
        if hip_avg_y - shoulder_avg_y > 0.1:  # Threshold value
            results["feedback"].append("Keep your back straight - don't let your hips sag")
            results["cheat_detected"] = True
            
        # Check if elbows are flaring out too much
        left_elbow = landmarks.landmark[13]
        right_elbow = landmarks.landmark[14]
        
        # Simple check: elbows should not be too far from body
        if abs(left_elbow.x - 0.5) > 0.3 or abs(right_elbow.x - 0.5) > 0.3:
            results["feedback"].append("Keep your elbows closer to your body")
    
    def _calculate_final_metrics(self, results, test_type):
        """Calculate final performance metrics"""
        if test_type == "pushups":
            reps = results["metrics"].get("repetitions", 0)
            angles = results["metrics"].get("elbow_angles", [])
            
            if angles:
                avg_depth = 180 - np.mean(angles)  # Lower angle = deeper pushup
                consistency = np.std(angles)  # Lower std = more consistent form
                
                # Calculate score based on reps, depth, and consistency
                score = min(100, reps * 10)  # Base score from reps
                score *= (1 + (avg_depth / 90))  # Reward depth
                score *= (1 - (consistency / 180))  # Penalize inconsistency
                
                results["ai_score"] = min(100, score)
                results["metrics"]["average_depth"] = avg_depth
                results["metrics"]["form_consistency"] = consistency
                
                # Generate performance feedback
                if reps == 0:
                    results["feedback"].append("No complete repetitions detected")
                elif reps < 5:
                    results["feedback"].append(f"Completed {reps} repetitions - keep practicing!")
                else:
                    results["feedback"].append(f"Great job! Completed {reps} repetitions")
                    
                if avg_depth < 45:
                    results["feedback"].append("Try to go deeper in your pushups for full range of motion")
                    
                if consistency > 20:
                    results["feedback"].append("Work on maintaining consistent form throughout your set")
