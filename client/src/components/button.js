// Modified from ShadCN
import React from "react";

export function Button({ children, className, ...props }) {
    return (
        <button
            className={`px-4 py-2 bg-[#2f53bd] hover:bg-[#4169E1] text-[#EEEBE3] font-medium rounded-lg transition-all duration-200 shadow-md disabled:opacity-50 disabled:cursor-not-allowed ${className}`}
            {...props}
        >
            {children}
        </button>
    );
}

