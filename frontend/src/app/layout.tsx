import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";
import { ErrorBoundary } from "@/components/ErrorBoundary";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "GymFlow AI | Elite AI-Powered Gym Operating System",
  description:
    "The world's most advanced AI-powered gym management platform. Real-time voice coaching, posture analysis, and automated operations for elite fitness centers.",
  keywords: [
    "gym management software",
    "AI fitness coach",
    "computer vision fitness",
    "SaaS for gyms",
    "automated workout tracking",
    "GymFlow AI",
  ],
  authors: [{ name: "GymFlow AI Team" }],
  openGraph: {
    type: "website",
    locale: "en_US",
    url: "https://gymflowai.com",
    title: "GymFlow AI | Elite AI-Powered Gym OS",
    description: "Transform your gym with real-time AI coaching and posture analysis.",
    siteName: "GymFlow AI",
  },
  twitter: {
    card: "summary_large_image",
    title: "GymFlow AI | Elite AI-Powered Gym OS",
    description: "Transform your gym with real-time AI coaching and posture analysis.",
    creator: "@gymflowai",
  },
};

export const viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased dark`}
    >
      <body className="min-h-full flex flex-col bg-background text-foreground transition-colors duration-300">
        <ErrorBoundary>
          <Providers>{children}</Providers>
        </ErrorBoundary>
      </body>
    </html>
  );
}


