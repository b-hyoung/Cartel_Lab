"use client";

import { useSession, signIn } from "next-auth/react";
import { useEffect } from "react";

export default function DevAutoLogin() {
  const { data: session, status } = useSession();

  useEffect(() => {
    if (status === "unauthenticated" && process.env.NEXT_PUBLIC_DEV_AUTO_LOGIN === "true") {
      signIn("credentials", {
        student_id: "dev",
        password: "dev1234",
        redirect: false,
      });
    }
  }, [status, session]);

  return null;
}
