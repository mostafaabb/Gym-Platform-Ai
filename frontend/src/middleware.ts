import { NextRequest, NextResponse } from "next/server";

// Public routes that don't require authentication
const PUBLIC_ROUTES = ["/", "/auth/login", "/auth/register", "/auth/forgot-password", "/auth/reset-password"];

// Routes that should only be accessible without authentication
const AUTH_ONLY_ROUTES = ["/auth/login", "/auth/register", "/auth/forgot-password", "/auth/reset-password"];

// Protected routes that require authentication
const PROTECTED_ROUTES = ["/dashboard", "/member", "/admin"];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get("access_token")?.value;

  console.log(`Middleware: ${pathname}, hasToken: ${!!token}`);

  // Check if route is public
  const isPublicRoute = PUBLIC_ROUTES.some((route) =>
    pathname === "/" || pathname.startsWith(route)
  );

  // Check if route is auth only (login/register)
  const isAuthOnlyRoute = AUTH_ONLY_ROUTES.some((route) =>
    pathname.startsWith(route)
  );

  // Check if route is protected (dashboard)
  const isProtectedRoute = PROTECTED_ROUTES.some((route) =>
    pathname.startsWith(route)
  );

  // 1. If user has token and tries to access auth-only routes (login/register), 
  // redirect them to the member dashboard (or you could fetch role here if needed)
  if (token && isAuthOnlyRoute) {
    return NextResponse.redirect(new URL("/dashboard/member", request.url));
  }

  // 2. If user doesn't have token and tries to access protected routes, redirect to login
  if (!token && isProtectedRoute) {
    const loginUrl = new URL("/auth/login", request.url);
    loginUrl.searchParams.set("from", pathname);
    return NextResponse.redirect(loginUrl);
  }

  // Allow the request to proceed
  return NextResponse.next();
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    "/((?!_next/static|_next/image|favicon.ico).*)",
  ],
};
