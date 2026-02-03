import { auth } from "@/auth"

export default auth((req) => {
    // complex logic handled in auth.ts callback
})

// Optionally, don't invoke Middleware on some paths
export const config = {
    matcher: ["/((?!api|_next/static|_next/image|favicon.ico).*)"],
}
