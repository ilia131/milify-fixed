"use client";

import images from "@/public/images";

import {
  PlayCircle,
  X,
  Headphones,
  Send,
} from "lucide-react";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";

import {
  ToastProvider,
  useToast,
} from "@/components/ToastProvider/ToastProvider";

import { useCreateSupportRequestMutation } from "@/redux/services/supportApi";

function HomeContent() {
  const [position, setPosition] = useState({
    x: 0,
    y: 0,
  });

  const [isSupportOpen, setIsSupportOpen] =
    useState(false);

  const [email, setEmail] = useState("");
  const [subject, setSubject] = useState("");
  const [message, setMessage] = useState("");

  const { success, error: showError } = useToast();

  const [
    createSupportRequest,
    { isLoading },
  ] = useCreateSupportRequestMutation();

  const handleSubmitSupport = async (
    e: React.FormEvent<HTMLFormElement>
  ) => {
    e.preventDefault();

    const trimmedEmail = email.trim();
    const trimmedSubject = subject.trim();
    const trimmedMessage = message.trim();

    try {
      await createSupportRequest({
        email: trimmedEmail || undefined,
        subject: trimmedSubject,
        message: trimmedMessage,
      }).unwrap();

      // Reset form
      setEmail("");
      setSubject("");
      setMessage("");

      // Close modal
      setIsSupportOpen(false);

      // Success Toast
      success(
        "درخواست پشتیبانی با موفقیت ارسال شد."
      );
    } catch (error) {
      console.error(
        "Support request error:",
        error
      );

      // Error Toast
      showError(
        "ارسال درخواست با مشکل مواجه شد. دوباره تلاش کنید."
      );
    }
  };

  return (
    <main
      onMouseMove={(e) =>
        setPosition({
          x: e.clientX,
          y: e.clientY,
        })
      }
      className="relative min-h-screen overflow-hidden bg-[#070707] text-white"
    >
      {/* ================= Mouse Glow ================= */}

      <div
        className="
          pointer-events-none
          absolute
          z-0
          hidden
          h-[500px]
          w-[500px]
          rounded-full
          bg-green-500/20
          blur-[180px]
          transition-all
          duration-300
          lg:block
        "
        style={{
          left: position.x - 250,
          top: position.y - 250,
        }}
      />

      {/* ================= Aurora Background ================= */}

      <div className="absolute inset-0 overflow-hidden">
        <div
          className="
            absolute
            left-[-10%]
            top-[-20%]
            h-[400px]
            w-[400px]
            rounded-full
            bg-green-500/20
            blur-[140px]
          "
        />

        <div
          className="
            absolute
            right-[-10%]
            top-[10%]
            h-[350px]
            w-[350px]
            rounded-full
            bg-violet-500/20
            blur-[140px]
          "
        />

        <div
          className="
            absolute
            bottom-[-20%]
            left-[30%]
            h-[450px]
            w-[450px]
            rounded-full
            bg-cyan-500/10
            blur-[180px]
          "
        />
      </div>

      {/* ================= Navbar ================= */}

      <header className="fixed top-0 z-50 w-full">
        <div
          className="
            mx-auto
            flex
            max-w-7xl
            items-center
            justify-between
            px-5
            py-5
          "
        >
          {/* Logo */}

          <div
            className="
              rounded-full
              border
              border-white/10
              bg-white/5
              px-5
              py-2
              backdrop-blur-xl
            "
          >
            <h1 className="text-lg font-black tracking-wider">
              MILIFY
            </h1>
          </div>

          <div className="flex items-center gap-3">
            {/* Support */}

          

            {/* Open App */}

            <Link
              href="/auth/login"
              className="
                rounded-full
                bg-green-500
                px-5
                py-3
                text-sm
                font-semibold
                text-black
                transition
                hover:scale-105
              "
            >
              Open App
            </Link>
          </div>
        </div>
      </header>

      {/* ================= Hero ================= */}

      <section
        className="
          relative
          z-10
          flex
          min-h-screen
          items-center
          px-6
          py-32
        "
      >
        <div
          className="
            mx-auto
            grid
            max-w-7xl
            items-center
            gap-16
            lg:grid-cols-2
          "
        >
          {/* ================= Left ================= */}

          <div
            className="
              order-2
              text-center
              lg:order-1
              lg:text-left
            "
          >
            <span
              className="
                inline-flex
                rounded-full
                border
                border-white/10
                bg-white/5
                px-4
                py-2
                text-sm
                backdrop-blur-xl
              "
            >
              🎵 Future Of Music
            </span>

            <h1
              className="
                mt-6
                text-5xl
                font-black
                leading-tight
                sm:text-6xl
                lg:text-7xl
              "
            >
              Music
              <br />
              Beyond
              <span
                className="
                  bg-gradient-to-r
                  from-green-400
                  to-cyan-400
                  bg-clip-text
                  text-transparent
                "
              >
                {" "}
                Streaming
              </span>
            </h1>

            <p
              className="
                mx-auto
                mt-6
                max-w-xl
                text-base
                text-zinc-400
                sm:text-lg
                lg:mx-0
              "
            >
              Discover millions of songs,
              immersive playlists and futuristic
              audio experiences in one beautiful
              platform.
            </p>

            <div
              className="
                mt-8
                flex
                flex-col
                justify-center
                gap-4
                sm:flex-row
                lg:justify-start
              "
            >
              {/* Start Listening */}

              <Link
                href="/auth/login"
                className="
                  rounded-full
                  bg-green-500
                  px-8
                  py-4
                  font-semibold
                  text-black
                  transition
                  hover:scale-105
                "
              >
                Start Listening
              </Link>

              {/* Get Support */}

              <button
                type="button"
                onClick={() =>
                  setIsSupportOpen(true)
                }
                className="
                  flex
                  items-center
                  justify-center
                  gap-2
                  rounded-full
                  border
                  border-white/10
                  bg-white/5
                  px-8
                  py-4
                  backdrop-blur-xl
                  transition
                  hover:bg-white/10
                "
              >
                <Headphones size={18} />

                Get Support
              </button>
            </div>
          </div>

          {/* ================= Right ================= */}

          <div
            className="
              order-1
              flex
              items-center
              justify-center
              lg:order-2
              lg:justify-end
            "
          >
            <div className="relative">
              {/* Music Card */}

              <div
                className="
                  animate-float
                  rounded-[32px]
                  border
                  border-white/10
                  bg-white/5
                  p-4
                  backdrop-blur-3xl
                  sm:p-6
                "
              >
                <Image
                  src={images.dorcci2}
                  alt="Album"
                  width={220}
                  height={220}
                  className="
                    aspect-square
                    w-[220px]
                    rounded-3xl
                    object-cover
                    sm:w-[280px]
                    lg:w-[320px]
                  "
                />

                <div className="mt-5">
                  <h3 className="text-lg font-bold">
                    Be Koja Residi
                  </h3>

                  <p className="text-sm text-zinc-400">
                    Dorcci
                  </p>
                </div>

                {/* Progress */}

                <div
                  className="
                    mt-5
                    h-1
                    rounded-full
                    bg-white/10
                  "
                >
                  <div
                    className="
                      h-full
                      w-2/3
                      rounded-full
                      bg-green-400
                    "
                  />
                </div>

                {/* Controls */}

                <div
                  className="
                    mt-5
                    flex
                    items-center
                    justify-center
                    gap-6
                    text-xl
                  "
                >
                  <button type="button">
                    ⏮
                  </button>

                  <PlayCircle />

                  <button type="button">
                    ⏭
                  </button>
                </div>
              </div>

              {/* Equalizer */}

              <div
                className="
                  absolute
                  -left-10
                  top-1/2
                  hidden
                  -translate-y-1/2
                  gap-2
                  md:flex
                "
              >
                {[40, 70, 90, 50, 80].map(
                  (height, index) => (
                    <div
                      key={index}
                      style={{ height }}
                      className="
                        w-2
                        animate-pulse
                        rounded-full
                        bg-green-400
                      "
                    />
                  )
                )}
              </div>

              {/* Floating Music Icon */}

              <div
                className="
                  absolute
                  -right-4
                  top-6
                  rounded-2xl
                  border
                  border-white/10
                  bg-white/10
                  p-3
                  text-2xl
                  backdrop-blur-xl
                "
              >
                🎵
              </div>

              {/* Floating Headphone Icon */}

              <div
                className="
                  absolute
                  -left-4
                  bottom-8
                  rounded-2xl
                  border
                  border-white/10
                  bg-white/10
                  p-3
                  text-2xl
                  backdrop-blur-xl
                "
              >
                🎧
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ================= Support Modal ================= */}

      {isSupportOpen && (
        <div
          className="
            fixed
            inset-0
            z-[100]
            flex
            items-center
            justify-center
            bg-black/70
            px-5
            backdrop-blur-md
          "
          onMouseDown={() =>
            setIsSupportOpen(false)
          }
        >
          <div
            onMouseDown={(e) =>
              e.stopPropagation()
            }
            className="
              relative
              w-full
              max-w-lg
              rounded-[28px]
              border
              border-white/10
              bg-[#101010]/95
              p-6
              shadow-2xl
              backdrop-blur-2xl
              sm:p-8
            "
          >
            {/* Close */}

            <button
              type="button"
              onClick={() =>
                setIsSupportOpen(false)
              }
              className="
                absolute
                right-5
                top-5
                rounded-full
                p-2
                text-zinc-400
                transition
                hover:bg-white/10
                hover:text-white
              "
              aria-label="Close support modal"
            >
              <X size={20} />
            </button>

            {/* Header */}

            <div className="mb-7">
              <div
                className="
                  mb-4
                  flex
                  h-12
                  w-12
                  items-center
                  justify-center
                  rounded-2xl
                  bg-green-500/10
                  text-green-400
                "
              >
                <Headphones size={24} />
              </div>

              <h2 className="text-2xl font-bold">
                How can we help?
              </h2>

              <p className="mt-2 text-sm text-zinc-400">
                Send us your question and our
                support team will get back to you.
              </p>
            </div>

            {/* ================= Form ================= */}

            <form
              onSubmit={handleSubmitSupport}
              className="space-y-4"
            >
              {/* Email */}

              <div>
                <label
                  className="
                    mb-2
                    block
                    text-sm
                    text-zinc-300
                  "
                >
                  Email

                  <span className="ml-1 text-zinc-500">
                    (optional)
                  </span>
                </label>

                <input
                  type="email"
                  value={email}
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }
                  placeholder="you@example.com"
                  className="
                    w-full
                    rounded-2xl
                    border
                    border-white/10
                    bg-white/5
                    px-4
                    py-3.5
                    text-sm
                    outline-none
                    transition
                    placeholder:text-zinc-600
                    focus:border-green-500/50
                    focus:bg-white/[0.07]
                  "
                />
              </div>

              {/* Subject */}

              <div>
                <label
                  className="
                    mb-2
                    block
                    text-sm
                    text-zinc-300
                  "
                >
                  Subject
                </label>

                <input
                  type="text"
                  required
                  minLength={3}
                  value={subject}
                  onChange={(e) =>
                    setSubject(e.target.value)
                  }
                  placeholder="What is the problem?"
                  className="
                    w-full
                    rounded-2xl
                    border
                    border-white/10
                    bg-white/5
                    px-4
                    py-3.5
                    text-sm
                    outline-none
                    transition
                    placeholder:text-zinc-600
                    focus:border-green-500/50
                    focus:bg-white/[0.07]
                  "
                />
              </div>

              {/* Message */}

              <div>
                <label
                  className="
                    mb-2
                    block
                    text-sm
                    text-zinc-300
                  "
                >
                  Message
                </label>

                <textarea
                  required
                  minLength={10}
                  value={message}
                  onChange={(e) =>
                    setMessage(e.target.value)
                  }
                  placeholder="Tell us what happened..."
                  rows={5}
                  className="
                    w-full
                    resize-none
                    rounded-2xl
                    border
                    border-white/10
                    bg-white/5
                    px-4
                    py-3.5
                    text-sm
                    outline-none
                    transition
                    placeholder:text-zinc-600
                    focus:border-green-500/50
                    focus:bg-white/[0.07]
                  "
                />

                <p className="mt-1 text-xs text-zinc-600">
                  Minimum 10 characters
                </p>
              </div>

              {/* Submit */}

              <button
                type="submit"
                disabled={isLoading}
                className="
                  flex
                  w-full
                  items-center
                  justify-center
                  gap-2
                  rounded-2xl
                  bg-green-500
                  py-4
                  font-semibold
                  text-black
                  transition
                  hover:bg-green-400
                  disabled:cursor-not-allowed
                  disabled:opacity-50
                "
              >
                {isLoading ? (
                  <>
                    <span
                      className="
                        h-5
                        w-5
                        animate-spin
                        rounded-full
                        border-2
                        border-black/30
                        border-t-black
                      "
                    />

                    Sending...
                  </>
                ) : (
                  <>
                    <Send size={18} />

                    Send Request
                  </>
                )}
              </button>
            </form>
          </div>
        </div>
      )}
    </main>
  );
}

export default function HomePage() {
  return (
    <ToastProvider>
      <HomeContent />
    </ToastProvider>
  );
}