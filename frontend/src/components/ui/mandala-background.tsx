"use client";

import React from "react";

/**
 * Exact Mandala Background Component implementing Left and Right SVGs
 * as specified in the exact design instructions.
 */
export function MandalaBackground() {
  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 overflow-hidden select-none"
    >
      {/* MANDALA A — LEFT */}
      <svg className="mandala-left" viewBox="0 0 600 600" aria-hidden="true">
        <g
          transform="translate(300 300)"
          fill="none"
          stroke="#2A1503"
          strokeWidth="2"
        >
          <defs>
            <path
              id="avasarOuterPetal"
              d="M0,-260 C45,-200 45,-100 0,-40 C-45,-100 -45,-200 0,-260 Z"
            />
          </defs>

          <g>
            <use href="#avasarOuterPetal" />
            <use href="#avasarOuterPetal" transform="rotate(20)" />
            <use href="#avasarOuterPetal" transform="rotate(40)" />
            <use href="#avasarOuterPetal" transform="rotate(60)" />
            <use href="#avasarOuterPetal" transform="rotate(80)" />
            <use href="#avasarOuterPetal" transform="rotate(100)" />
            <use href="#avasarOuterPetal" transform="rotate(120)" />
            <use href="#avasarOuterPetal" transform="rotate(140)" />
            <use href="#avasarOuterPetal" transform="rotate(160)" />
            <use href="#avasarOuterPetal" transform="rotate(180)" />
            <use href="#avasarOuterPetal" transform="rotate(200)" />
            <use href="#avasarOuterPetal" transform="rotate(220)" />
            <use href="#avasarOuterPetal" transform="rotate(240)" />
            <use href="#avasarOuterPetal" transform="rotate(260)" />
            <use href="#avasarOuterPetal" transform="rotate(280)" />
            <use href="#avasarOuterPetal" transform="rotate(300)" />
            <use href="#avasarOuterPetal" transform="rotate(320)" />
            <use href="#avasarOuterPetal" transform="rotate(340)" />
          </g>

          <circle r="200" stroke="#8B4513" />
          <circle r="160" stroke="#000000" />
          <circle r="120" stroke="#C19A6B" />
          <circle r="90" />
          <circle r="65" />
          <circle r="40" />
          <circle r="12" fill="#2A1503" />
        </g>
      </svg>

      {/* MANDALA B — RIGHT */}
      <svg className="mandala-right" viewBox="0 0 600 600" aria-hidden="true">
        <g
          transform="translate(300 300)"
          fill="none"
          stroke="#2A1503"
          strokeWidth="2"
        >
          <defs>
            <path
              id="avasarOuterPetalSmall"
              d="M0,-200 C35,-150 35,-80 0,-30 C-35,-80 -35,-150 0,-200 Z"
            />
          </defs>

          <g>
            <use href="#avasarOuterPetalSmall" />
            <use href="#avasarOuterPetalSmall" transform="rotate(30)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(60)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(90)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(120)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(150)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(180)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(210)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(240)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(270)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(300)" />
            <use href="#avasarOuterPetalSmall" transform="rotate(330)" />
          </g>

          <circle r="150" stroke="#8B4513" />
          <circle r="110" stroke="#000000" />
          <circle r="12" fill="#2A1503" />
        </g>
      </svg>
    </div>
  );
}
