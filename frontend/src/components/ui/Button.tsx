import React, { ButtonHTMLAttributes, forwardRef } from "react";
import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "btn-base rounded-lg font-semibold focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed",
  {
    variants: {
      variant: {
        primary:
          "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500 dark:bg-blue-600 dark:hover:bg-blue-700",
        secondary:
          "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500 dark:bg-gray-700 dark:text-white dark:hover:bg-gray-600",
        destructive:
          "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500 dark:bg-red-600 dark:hover:bg-red-700",
        outline:
          "border-2 border-gray-300 text-gray-900 hover:bg-gray-100 focus:ring-gray-500 dark:border-gray-600 dark:text-white dark:hover:bg-gray-800",
        ghost:
          "text-gray-900 hover:bg-gray-100 focus:ring-gray-500 dark:text-white dark:hover:bg-gray-800",
        link: "text-blue-600 hover:underline dark:text-blue-400",
      },
      size: {
        xs: "px-2 py-1 text-xs",
        sm: "px-3 py-1.5 text-sm",
        md: "px-4 py-2 text-base",
        lg: "px-6 py-3 text-lg",
        xl: "px-8 py-4 text-xl",
      },
      fullWidth: {
        true: "w-full",
      },
      loading: {
        true: "opacity-70 cursor-not-allowed",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  isLoading?: boolean;
  icon?: React.ReactNode;
}

const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  (
    {
      className,
      variant,
      size,
      fullWidth,
      isLoading,
      icon,
      disabled,
      children,
      ...props
    },
    ref
  ) => {
    return (
      <button
        ref={ref}
        disabled={disabled || isLoading}
        className={cn(
          buttonVariants({ variant, size, fullWidth, loading: isLoading }),
          className
        )}
        {...props}
      >
        <div className="flex items-center justify-center gap-2">
          {isLoading && (
            <div className="animate-spin">
              <svg
                className="h-4 w-4"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
            </div>
          )}
          {icon && !isLoading && <span>{icon}</span>}
          {children}
        </div>
      </button>
    );
  }
);

Button.displayName = "Button";

export { Button, buttonVariants };
