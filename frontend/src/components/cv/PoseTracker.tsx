"use client";

import React, { useRef, useEffect } from "react";

interface PoseTrackerProps {
  onLandmarksUpdate?: (landmarks: any) => void;
  isActive: boolean;
}

const PoseTracker: React.FC<PoseTrackerProps> = ({ onLandmarksUpdate, isActive }) => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const cameraRef = useRef<any>(null);

  useEffect(() => {
    if (!isActive) {
      if (cameraRef.current) {
        cameraRef.current.stop();
      }
      return;
    }

    // Initialize MediaPipe dynamically to avoid build-time import issues
    let pose: any;
    let cam: any;
    let draw: any;

    const initPose = async () => {
      try {
        // Use require for legacy MediaPipe packages to bypass ES module issues
        const PoseLib = require("@mediapipe/pose");
        const CamLib = require("@mediapipe/camera_utils");
        const DrawLib = require("@mediapipe/drawing_utils");

        // MediaPipe packages sometimes export differently depending on environment
        const Pose = PoseLib.Pose || (window as any).Pose;
        cam = CamLib;
        draw = DrawLib;

        pose = new Pose({
          locateFile: (file: string) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
          },
        });

        pose.setOptions({
          modelComplexity: 1,
          smoothLandmarks: true,
          enableSegmentation: false,
          smoothSegmentation: false,
          minDetectionConfidence: 0.5,
          minTrackingConfidence: 0.5,
        });

        pose.onResults((results: any) => {
          if (!canvasRef.current || !videoRef.current) return;

          const canvasCtx = canvasRef.current.getContext("2d");
          if (!canvasCtx) return;

          canvasCtx.save();
          canvasCtx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
          
          if (results.poseLandmarks) {
            // drawing_utils functions are often attached directly to the module
            const drawConnectors = draw.drawConnectors || (window as any).drawConnectors;
            const drawLandmarks = draw.drawLandmarks || (window as any).drawLandmarks;

            if (drawConnectors) {
              drawConnectors(canvasCtx, results.poseLandmarks, PoseLib.POSE_CONNECTIONS || [[11,12], [11,13], [13,15], [12,14], [14,16], [11,23], [12,24], [23,24], [23,25], [25,27], [24,26], [26,28]], {
                color: "#3b82f6",
                lineWidth: 4,
              });
            }
            if (drawLandmarks) {
              drawLandmarks(canvasCtx, results.poseLandmarks, {
                color: "#ffffff",
                lineWidth: 2,
                radius: 4,
              });
            }
            
            if (onLandmarksUpdate) {
              onLandmarksUpdate(results.poseLandmarks);
            }
          }
          canvasCtx.restore();
        });

        if (videoRef.current) {
          const Camera = cam.Camera || (window as any).Camera;
          cameraRef.current = new Camera(videoRef.current, {
            onFrame: async () => {
              if (videoRef.current && pose) {
                await pose.send({ image: videoRef.current });
              }
            },
            width: 1280,
            height: 720,
          });
          cameraRef.current.start();
        }
      } catch (err) {
        console.error("Failed to initialize Pose Engine:", err);
      }
    };

    initPose();

    return () => {
      if (cameraRef.current) {
        cameraRef.current.stop();
      }
      if (pose) {
        pose.close();
      }
    };
  }, [isActive, onLandmarksUpdate]);

  return (
    <div className="relative h-full w-full overflow-hidden rounded-3xl bg-black">
      <video
        ref={videoRef}
        className="absolute inset-0 h-full w-full object-cover opacity-60"
        playsInline
        muted
      />
      <canvas
        ref={canvasRef}
        className="absolute inset-0 h-full w-full object-cover"
        width={1280}
        height={720}
      />
      
      {/* Decorative Overlays */}
      <div className="absolute inset-0 pointer-events-none border-[1px] border-white/10" />
      <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-[10px] font-bold uppercase tracking-widest backdrop-blur-md">
         <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
         Pose Engine Active
      </div>
    </div>
  );
};

export default PoseTracker;
