import React from 'react';
import { cn } from '@/lib/utils';

export function SkeletonLoader({ className, ...props }: React.HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn("animate-pulse rounded-md bg-muted", className)}
      {...props}
    />
  );
}

export function CardSkeleton() {
  return (
    <div className="flex flex-col space-y-3">
      <SkeletonLoader className="h-[125px] w-[250px] rounded-xl" />
      <div className="space-y-2">
        <SkeletonLoader className="h-4 w-[250px]" />
        <SkeletonLoader className="h-4 w-[200px]" />
      </div>
    </div>
  );
}
