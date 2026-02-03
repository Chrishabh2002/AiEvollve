"use server";

import { signIn } from "@/auth";

export async function handleCredentialsLogin(formData: FormData) {
    await signIn("credentials", formData);
}
