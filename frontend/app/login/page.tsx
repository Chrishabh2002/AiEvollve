import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button"; // Added Button
import Link from "next/link";
import Logo from "@/components/Logo";
import GoogleLoginButton from "@/components/GoogleAuthButton";
import { handleCredentialsLogin } from "./action";

export default function LoginPage() {
    return (
        <div className="flex min-h-screen flex-col items-center justify-center p-4 bg-background">
            <div className="absolute top-8 left-8">
                <Link href="/">
                    <Logo />
                </Link>
            </div>
            <div className="w-full max-w-sm space-y-6">
                <div className="space-y-2 text-center">
                    <h1 className="text-3xl font-bold tracking-tight">Welcome back</h1>
                    <p className="text-muted-foreground">Enter your credentials to access the world</p>
                </div>

                <div className="space-y-4">
                    <GoogleLoginButton text="Sign in with Google" />

                    <div className="relative">
                        <div className="absolute inset-0 flex items-center">
                            <span className="w-full border-t" />
                        </div>
                        <div className="relative flex justify-center text-xs uppercase">
                            <span className="bg-background px-2 text-muted-foreground">Or continue with</span>
                        </div>
                    </div>

                    {/* Manual Form - Now Active */}
                    <form action={handleCredentialsLogin} className="space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium leading-none" htmlFor="email">Email</label>
                            <Input id="email" name="email" placeholder="m@example.com" type="email" required />
                        </div>
                        <div className="space-y-2">
                            <div className="flex items-center justify-between">
                                <label className="text-sm font-medium leading-none" htmlFor="password">Password</label>
                            </div>
                            <Input id="password" name="password" type="password" required />
                        </div>
                        <Button className="w-full" type="submit">Email Login</Button>
                    </form>
                </div>

                <div className="text-center text-sm">
                    Don&apos;t have an account?{" "}
                    <Link className="underline underline-offset-4 hover:text-primary" href="/signup">
                        Sign up
                    </Link>
                </div>
            </div>
        </div>
    );
}
