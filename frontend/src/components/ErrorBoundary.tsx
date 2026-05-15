"use client";

import React, { Component, ErrorInfo, ReactNode } from "react";
import { AlertTriangle, RefreshCw, Home } from "lucide-react";
import Link from "next/link";
import { Button } from "./ui/Button";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null,
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 p-6 text-center">
          <div className="mb-8 flex h-24 w-24 items-center justify-center rounded-full bg-red-500/10 text-red-500 shadow-2xl shadow-red-500/20">
            <AlertTriangle size={48} />
          </div>
          <h1 className="mb-4 text-4xl font-bold tracking-tight text-white">Something went wrong</h1>
          <p className="mb-8 max-w-md text-zinc-400">
            An unexpected error occurred in the application. We've been notified and are looking into it.
          </p>
          <div className="flex flex-col gap-4 sm:flex-row">
            <Button
              onClick={() => window.location.reload()}
              className="btn-primary flex items-center gap-2"
            >
              <RefreshCw size={18} />
              Reload Page
            </Button>
            <Link href="/">
              <Button variant="outline" className="h-12 border-white/10 text-white hover:bg-white/5 flex items-center gap-2">
                <Home size={18} />
                Back to Home
              </Button>
            </Link>
          </div>
          {process.env.NODE_ENV === "development" && this.state.error && (
            <div className="mt-12 max-w-2xl overflow-auto rounded-xl border border-red-500/20 bg-red-500/5 p-6 text-left font-mono text-xs text-red-400">
              <p className="mb-2 font-bold uppercase tracking-widest text-red-500/50">Error Detail:</p>
              {this.state.error.toString()}
            </div>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}
