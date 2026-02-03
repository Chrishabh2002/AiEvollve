
import NextAuth from "next-auth"
import Google from "next-auth/providers/google"
import Credentials from "next-auth/providers/credentials"

export const { handlers, signIn, signOut, auth } = NextAuth({
    providers: [
        Google,
        Credentials({
            name: "Credentials",
            credentials: {
                email: { label: "Email", type: "email" },
                password: { label: "Password", type: "password" }
            },
            async authorize(credentials) {
                // MOCK AUTH LOGIC
                // In a real app, you would verify against a DB here.
                // For this demo, we accept any "admin" user or just let them in.

                if (credentials?.email && credentials?.password) {
                    return {
                        id: "mock-user-id",
                        name: "Demo User",
                        email: credentials.email as string,
                        image: "https://api.dicebear.com/7.x/avataaars/svg?seed=Felix"
                    };
                }
                return null;
            }
        })
    ],
    callbacks: {
        authorized({ auth, request: { nextUrl } }) {
            const isLoggedIn = !!auth?.user;
            const isOnWorld = nextUrl.pathname.startsWith('/world');

            if (isOnWorld) {
                if (isLoggedIn) return true;
                return false; // Redirect unauthenticated users to login page
            } else if (isLoggedIn) {
                if (nextUrl.pathname === '/login' || nextUrl.pathname === '/signup') {
                    return Response.redirect(new URL('/world', nextUrl));
                }
            }
            return true;
        },
        async session({ session, token }) {
            return session;
        },
    },
    pages: {
        signIn: '/login',
        error: '/login',
    },
})
