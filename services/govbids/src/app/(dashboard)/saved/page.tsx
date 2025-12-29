import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import { SavedContracts } from "./saved-contracts";

export default function SavedPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Saved Contracts</h1>
        <p className="text-muted-foreground mt-1">
          Contracts you&apos;re tracking
        </p>
      </div>

      <Suspense
        fallback={
          <div className="space-y-4">
            {[...Array(3)].map((_, i) => (
              <Skeleton key={i} className="h-32" />
            ))}
          </div>
        }
      >
        <SavedContracts />
      </Suspense>
    </div>
  );
}
