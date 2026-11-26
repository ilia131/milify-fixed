"use client";

import { useMemo, useState } from "react";
import Image from "next/image";
import Link from "next/link";

import { useLoginMutation, useRegisterMutation } from "@/redux/services/authApiSlice";
import { useGetArtistsListQuery } from "@/redux/services/artistApislice";

import useSpotifyRouter from "@/hooks/authhooks/useSpotifyRouter";
import { useToast } from "@/components/ToastProvider/ToastProvider";

import { saveSession } from "@/hooks/authhooks/use-login";
import { useAppDispatch } from "@/redux/hook";

type Artist = {
  id: number;
  artistname: string;
  profile_pic?: string | null;
};

type RegisterFormData = {
  first_name: string;
  last_name: string;
  username: string;
  email: string;
  password: string;
  re_password: string;
  favorite_artists: string[];
};

const INITIAL_FORM: RegisterFormData = {
  first_name: "",
  last_name: "",
  username: "",
  email: "",
  password: "",
  re_password: "",
  favorite_artists: [],
};

export default function RegisterPage() {
  const [step, setStep] = useState<1 | 2>(1);
  const [formData, setFormData] =
    useState<RegisterFormData>(INITIAL_FORM);

  const [artistQuery, setArtistQuery] = useState("");

  const { replace } = useSpotifyRouter();
  const { success, error } = useToast();

  const [register, { isLoading: isRegistering }] = useRegisterMutation();
  const [login, { isLoading: isLoggingIn }] = useLoginMutation();
  const dispatch = useAppDispatch();
  const isLoading = isRegistering || isLoggingIn;

  const {
    data: artists = [],
    isLoading: artistsLoading,
  } = useGetArtistsListQuery(0);

  const filteredArtists = useMemo(() => {
    const query = artistQuery.trim().toLowerCase();

    if (!query) {
      return artists;
    }

    return artists.filter((artist: Artist) =>
      artist.artistname
        .toLowerCase()
        .includes(query)
    );
  }, [artistQuery, artists]);

  const updateField = (
    field: keyof Omit<
      RegisterFormData,
      "favorite_artists"
    >,
    value: string
  ) => {
    setFormData((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const toggleArtist = (artistName: string) => {
    setFormData((prev) => {
      const isSelected =
        prev.favorite_artists.includes(artistName);

      return {
        ...prev,
        favorite_artists: isSelected
          ? prev.favorite_artists.filter(
              (name) => name !== artistName
            )
          : [
              ...prev.favorite_artists,
              artistName,
            ],
      };
    });
  };

  const validateStepOne = () => {
    const requiredFields = [
      formData.first_name,
      formData.last_name,
      formData.username,
      formData.email,
      formData.password,
      formData.re_password,
    ];

    if (requiredFields.some((field) => !field.trim())) {
      error("Please fill in all required fields.");
      return false;
    }

    if (
      !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(
        formData.email
      )
    ) {
      error("Please enter a valid email address.");
      return false;
    }

    if (formData.password.length < 8) {
      error(
        "Password must be at least 8 characters."
      );
      return false;
    }

    if (
      formData.password !==
      formData.re_password
    ) {
      error("Passwords do not match.");
      return false;
    }

    return true;
  };

  const handleNextStep = (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    if (!validateStepOne()) {
      return;
    }

    setStep(2);
  };

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    try {
      await register(formData).unwrap();

    } catch (err: unknown) {
      const apiError = err as {
        data?: Record<
          string,
          string | string[]
        >;
      };

      if (apiError?.data) {
        const message = Object.values(
          apiError.data
        )
          .flat()
          .join("\n");

        error(message);
        return;
      }

      error("ثبت‌نام انجام نشد.");
      return;
    }

    try {
      const { email, password } = formData;
      const tokens = await login({ email: email.toLowerCase(), password }).unwrap();
      await saveSession(tokens, dispatch);
      success("ثبت‌نام موفق بود.");
      replace("/browse");
    } catch {
      error("حساب ایجاد شد. لطفاً وارد شوید.");
      replace("/auth/login");
    }
  };

  return (
    <main className="min-h-screen bg-[#121212] px-4 py-8 text-white">
      <div className="mx-auto flex min-h-[calc(100vh-4rem)] w-full max-w-xl items-center">
        <div className="w-full">

          {/* Header */}
          <header className="mb-8 text-center">
            <h1 className="text-3xl font-bold tracking-tight">
              Milify
            </h1>

            <p className="mt-2 text-sm text-gray-400">
              Create your account and personalize
              your music experience.
            </p>

            {/* Steps */}
            <div className="mx-auto mt-6 flex max-w-xs items-center justify-center gap-3">
              <StepIndicator
                step={1}
                active={step === 1}
                completed={step === 2}
              />

              <div className="h-px flex-1 bg-white/10" />

              <StepIndicator
                step={2}
                active={step === 2}
                completed={false}
              />
            </div>
          </header>

          {/* Card */}
          <section className="rounded-3xl border border-white/5 bg-[#181818] p-5 shadow-2xl sm:p-7">

            {step === 1 && (
              <AccountForm
                formData={formData}
                onChange={updateField}
                onSubmit={handleNextStep}
              />
            )}

            {step === 2 && (
              <ArtistSelection
                query={artistQuery}
                setQuery={setArtistQuery}
                artists={filteredArtists}
                loading={artistsLoading}
                selectedArtists={
                  formData.favorite_artists
                }
                onToggle={toggleArtist}
                onBack={() => setStep(1)}
                onSubmit={handleSubmit}
                isLoading={isLoading}
              />
            )}
          </section>

          {/* Login */}
          <div className="mt-6 text-center text-sm text-gray-400">
            Already have an account?{" "}
            <Link
              href="/auth/login"
              className="font-medium text-green-500 transition hover:text-green-400 hover:underline"
            >
              Log in
            </Link>
          </div>
        </div>
      </div>
    </main>
  );
}



function StepIndicator({
  step,
  active,
  completed,
}: {
  step: number;
  active: boolean;
  completed: boolean;
}) {
  return (
    <div
      className={`
        flex h-9 w-9 items-center justify-center
        rounded-full text-sm font-semibold
        transition
        ${
          active || completed
            ? "bg-green-500 text-black"
            : "bg-[#282828] text-gray-500"
        }
      `}
    >
      {completed ? "✓" : step}
    </div>
  );
}




function AccountForm({
  formData,
  onChange,
  onSubmit,
}: {
  formData: RegisterFormData;

  onChange: (
    field: keyof Omit<
      RegisterFormData,
      "favorite_artists"
    >,
    value: string
  ) => void;

  onSubmit: (
    event: React.FormEvent<HTMLFormElement>
  ) => void;
}) {
  return (
    <form
      onSubmit={onSubmit}
      className="space-y-5"
    >
      <div>
        <h2 className="text-xl font-semibold">
          Create your account
        </h2>

        <p className="mt-1 text-sm text-gray-400">
          Enter your account information.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <RegisterInput
          label="First name"
          name="first_name"
          value={formData.first_name}
          onChange={onChange}
        />

        <RegisterInput
          label="Last name"
          name="last_name"
          value={formData.last_name}
          onChange={onChange}
        />
      </div>

      <RegisterInput
        label="Username"
        name="username"
        value={formData.username}
        onChange={onChange}
      />

      <RegisterInput
        label="Email address"
        name="email"
        type="email"
        value={formData.email}
        onChange={onChange}
      />

      <RegisterInput
        label="Password"
        name="password"
        type="password"
        value={formData.password}
        onChange={onChange}
      />

      <RegisterInput
        label="Confirm password"
        name="re_password"
        type="password"
        value={formData.re_password}
        onChange={onChange}
      />

      <button
        type="submit"
        className="
          w-full rounded-full
          bg-green-500 py-3.5
          font-semibold text-black
          transition
          hover:bg-green-400
          active:scale-[0.98]
        "
      >
        Continue
      </button>
    </form>
  );
}


function RegisterInput({
  label,
  name,
  value,
  onChange,
  type = "text",
}: {
  label: string;
  name: keyof Omit<
    RegisterFormData,
    "favorite_artists"
  >;
  value: string;
  type?: string;

  onChange: (
    field: keyof Omit<
      RegisterFormData,
      "favorite_artists"
    >,
    value: string
  ) => void;
}) {
  return (
    <div>
      <label
        htmlFor={name}
        className="mb-2 block text-sm font-medium text-gray-300"
      >
        {label}
      </label>

      <input
        id={name}
        name={name}
        type={type}
        value={value}
        onChange={(event) =>
          onChange(
            name,
            event.target.value
          )
        }
        required
        className="
          w-full rounded-xl
          border border-white/5
          bg-[#242424]
          px-4 py-3
          text-white
          outline-none
          transition
          placeholder:text-gray-600
          focus:border-green-500/50
          focus:ring-2
          focus:ring-green-500/10
        "
      />
    </div>
  );
}


function ArtistSelection({
  query,
  setQuery,
  artists,
  loading,
  selectedArtists,
  onToggle,
  onBack,
  onSubmit,
  isLoading,
}: {
  query: string;
  setQuery: (value: string) => void;

  artists: Artist[];
  loading: boolean;

  selectedArtists: string[];

  onToggle: (artistName: string) => void;

  onBack: () => void;

  onSubmit: (
    event: React.FormEvent<HTMLFormElement>
  ) => void;

  isLoading: boolean;
}) {
  return (
    <form onSubmit={onSubmit} className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-semibold text-white">
          Choose your artists
        </h2>

        <p className="mt-1 text-sm text-gray-400">
          Select artists you want to follow.
        </p>
      </div>

      {/* Search */}
      <div className="relative">
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Search artists..."
          className="
            w-full
            rounded-full
            border border-white/5
            bg-white
            px-5 py-3
            text-black
            outline-none
            placeholder:text-gray-500
            focus:ring-2
            focus:ring-green-500
          "
        />
      </div>

      {/* Artists */}
      <div className="max-h-[420px] overflow-y-auto pr-1">
        {loading ? (
          <div className="flex min-h-40 items-center justify-center">
            <div
              className="
                h-8 w-8
                animate-spin
                rounded-full
                border-4
                border-white/10
                border-t-green-500
              "
            />
          </div>
        ) : artists.length === 0 ? (
          <div className="py-12 text-center text-sm text-gray-500">
            No artists found.
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 md:grid-cols-4">
            {artists.map((artist) => {
              const selected = selectedArtists.includes(
                artist.artistname
              );

              return (
                <button
                  key={artist.id}
                  type="button"
                  onClick={() => onToggle(artist.artistname)}
                  className="
                    group
                    flex
                    w-24
                    min-w-24
                    shrink-0
                    flex-col
                    items-center
                  "
                >
                  {/* Artist Image */}
                  <div
                    className="
                      relative
                      h-24
                      w-24
                      shrink-0
                      aspect-square
                    "
                  >
                    <Image
                      src={
                        artist.profile_pic ||
                        "/artist-placeholder.jpg"
                      }
                      alt={artist.artistname}
                      width={96}
                      height={96}
                      className={`
                        block
                        h-24
                        w-24
                        shrink-0
                        aspect-square
                        rounded-full
                        object-cover
                        transition-transform
                        duration-200
                        group-hover:scale-105
                        ${
                          selected
                            ? "ring-4 ring-green-500"
                            : "ring-1 ring-white/10"
                        }
                      `}
                    />

                    {/* Selected Overlay */}
                    {selected && (
                      <div
                        className="
                          absolute
                          inset-0
                          flex
                          items-center
                          justify-center
                          rounded-full
                          bg-green-500/30
                        "
                      >
                        <div
                          className="
                            flex
                            h-8
                            w-8
                            items-center
                            justify-center
                            rounded-full
                            bg-green-500
                            text-sm
                            font-bold
                            text-black
                            shadow-lg
                          "
                        >
                          ✓
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Artist Name */}
                  <span
                    className={`
                      mt-2
                      block
                      w-24
                      truncate
                      text-center
                      text-sm
                      transition-colors
                      ${
                        selected
                          ? "text-green-400"
                          : "text-gray-300"
                      }
                    `}
                  >
                    {artist.artistname}
                  </span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {/* Selected Artists */}
      {selectedArtists.length > 0 && (
        <div>
          <p
            className="
              mb-2
              text-xs
              font-medium
              uppercase
              tracking-wide
              text-gray-500
            "
          >
            Selected
          </p>

          <div className="flex flex-wrap gap-2">
            {selectedArtists.map((artist) => (
              <span
                key={artist}
                className="
                  rounded-full
                  bg-green-500/10
                  px-3
                  py-1.5
                  text-xs
                  text-green-400
                "
              >
                {artist}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3">
        {/* Back */}
        <button
          type="button"
          onClick={onBack}
          disabled={isLoading}
          className="
            w-1/2
            rounded-full
            bg-[#282828]
            py-3.5
            font-semibold
            text-white
            transition
            hover:bg-[#333]
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          Back
        </button>

        {/* Complete */}
        <button
          type="submit"
          disabled={isLoading}
          className="
            flex
            w-1/2
            items-center
            justify-center
            gap-2
            rounded-full
            bg-green-500
            py-3.5
            font-semibold
            text-black
            transition
            hover:bg-green-400
            disabled:cursor-not-allowed
            disabled:opacity-50
          "
        >
          {isLoading && (
            <span
              className="
                h-4
                w-4
                animate-spin
                rounded-full
                border-2
                border-black/30
                border-t-black
              "
            />
          )}

          {isLoading ? "Creating..." : "Complete"}
        </button>
      </div>
    </form>
  );
}