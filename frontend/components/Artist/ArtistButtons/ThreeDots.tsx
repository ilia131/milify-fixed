"use client";

import React from "react";

interface ThreeDotsProps {
  isAuthenticated: boolean;
  onClick?: (e: React.MouseEvent<HTMLDivElement>) => void;
  onRequireLogin?: () => void;
}

const ThreeDots = ({
  isAuthenticated,
  onClick,
  onRequireLogin,
}: ThreeDotsProps) => {
  const handleClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isAuthenticated) {
      onRequireLogin?.();
      return;
    }

    onClick?.(e);
  };

  return (
    <div
      className="flex h-5 w-4.75 cursor-pointer items-center justify-center"
      onClick={handleClick}
      role="button"
      tabIndex={0}
      aria-label="More options"
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();

          if (!isAuthenticated) {
            onRequireLogin?.();
            return;
          }

          onClick?.(
            e as unknown as React.MouseEvent<HTMLDivElement>
          );
        }
      }}
    >
      <svg
        xmlns="http://www.w3.org/2000/svg"
        width="19"
        height="3"
        viewBox="0 0 19 3"
        fill="none"
      >
        <circle
          cx="1.5"
          cy="1.5"
          r="1.5"
          fill="white"
          fillOpacity="0.78"
        />
        <circle
          cx="9.5"
          cy="1.5"
          r="1.5"
          fill="white"
          fillOpacity="0.78"
        />
        <circle
          cx="17.5"
          cy="1.5"
          r="1.5"
          fill="white"
          fillOpacity="0.78"
        />
      </svg>
    </div>
  );
};

export default ThreeDots;