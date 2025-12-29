import NextAuth from "next-auth";
import Credentials from "next-auth/providers/credentials";
import Google from "next-auth/providers/google";
import GitHub from "next-auth/providers/github";
import { z } from "zod";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

async function syncOAuthUser(
  email: string,
  name: string | null,
  provider: string
): Promise<{ accessToken: string; user: { id: string; email: string; name: string | null } }> {
  const response = await fetch(`${API_URL}/api/auth/oauth-sync`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Product-ID": "gov",
    },
    body: JSON.stringify({
      email,
      name,
      provider,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to sync OAuth user");
  }

  return response.json();
}

async function loginWithCredentials(
  email: string,
  password: string
): Promise<{ accessToken: string; user: { id: string; email: string; name: string | null } }> {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Product-ID": "gov",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error("Invalid credentials");
  }

  const data = await response.json();

  // Get user info with the token
  const meResponse = await fetch(`${API_URL}/api/auth/me`, {
    headers: {
      Authorization: `Bearer ${data.access_token}`,
      "X-Product-ID": "gov",
    },
  });

  if (!meResponse.ok) {
    throw new Error("Failed to get user info");
  }

  const user = await meResponse.json();

  return {
    accessToken: data.access_token,
    user: {
      id: user.id,
      email: user.email,
      name: user.name,
    },
  };
}

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID!,
      clientSecret: process.env.GITHUB_CLIENT_SECRET!,
    }),
    Credentials({
      name: "credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const parsed = loginSchema.safeParse(credentials);
        if (!parsed.success) {
          return null;
        }

        try {
          const result = await loginWithCredentials(
            parsed.data.email,
            parsed.data.password
          );

          return {
            id: result.user.id,
            email: result.user.email,
            name: result.user.name,
            accessToken: result.accessToken,
          };
        } catch {
          return null;
        }
      },
    }),
  ],
  pages: {
    signIn: "/login",
    error: "/login",
  },
  callbacks: {
    async signIn({ user, account }) {
      // For OAuth providers, sync user to backend
      if (account?.provider === "google" || account?.provider === "github") {
        try {
          const result = await syncOAuthUser(
            user.email!,
            user.name ?? null,
            account.provider
          );
          // Store the access token on the user object
          user.accessToken = result.accessToken;
          user.id = result.user.id;
        } catch {
          return false;
        }
      }
      return true;
    },
    async jwt({ token, user, account }) {
      // Initial sign in
      if (user) {
        token.id = user.id;
        token.email = user.email!;
        token.name = user.name;
        token.accessToken = user.accessToken;
      }

      // For OAuth, we need to sync on first sign in
      if (account && (account.provider === "google" || account.provider === "github") && token.email) {
        try {
          const result = await syncOAuthUser(
            token.email,
            token.name ?? null,
            account.provider
          );
          token.accessToken = result.accessToken;
          token.id = result.user.id;
        } catch {
          // Continue with existing token
        }
      }

      return token;
    },
    async session({ session, token }) {
      session.user.id = token.id as string;
      session.user.email = token.email as string;
      session.user.name = token.name as string | null | undefined;
      session.accessToken = token.accessToken as string | undefined;
      return session;
    },
  },
  session: {
    strategy: "jwt",
  },
});
