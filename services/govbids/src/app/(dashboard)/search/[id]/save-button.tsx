"use client";

import { useState } from "react";
import { Bookmark, BookmarkCheck, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { saveEntity, unsaveEntity } from "@/lib/api";
import { toast } from "sonner";

interface SaveButtonProps {
  contractId: string;
  accessToken?: string;
  initialSaved?: boolean;
}

export function SaveButton({
  contractId,
  accessToken,
  initialSaved = false,
}: SaveButtonProps) {
  const [isSaved, setIsSaved] = useState(initialSaved);
  const [isLoading, setIsLoading] = useState(false);

  const handleToggleSave = async () => {
    if (!accessToken) {
      toast.error("Please sign in to save contracts");
      return;
    }

    setIsLoading(true);
    try {
      if (isSaved) {
        await unsaveEntity(contractId, accessToken);
        setIsSaved(false);
        toast.success("Contract removed from saved");
      } else {
        await saveEntity(contractId, accessToken);
        setIsSaved(true);
        toast.success("Contract saved successfully");
      }
    } catch {
      toast.error("Failed to update saved status");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Button
      variant={isSaved ? "default" : "outline"}
      onClick={handleToggleSave}
      disabled={isLoading}
    >
      {isLoading ? (
        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
      ) : isSaved ? (
        <BookmarkCheck className="h-4 w-4 mr-2" />
      ) : (
        <Bookmark className="h-4 w-4 mr-2" />
      )}
      {isSaved ? "Saved" : "Save"}
    </Button>
  );
}
