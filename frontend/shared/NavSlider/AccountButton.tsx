import { useAppDispatch } from "@/redux/hook";
import { toggleMenu } from "@/redux/features/uiSlice";
import { useGetMyProfileQuery } from "@/redux/services/profileApiSlice";

interface AccountButtonProps {
  label?: string;
}

const AccountButton = ({ label }: AccountButtonProps) => {
  const dispatch = useAppDispatch();

  const { data: profile } = useGetMyProfileQuery();

  const emailInitial =
    profile?.email?.trim()?.charAt(0)?.toUpperCase() || "I";

  const displayLabel = label || emailInitial;

  return (
    <button
      onClick={() => dispatch(toggleMenu())}
      className="h-8.5 w-8.25 flex items-center justify-center"
      aria-label="Account"
    >
      <div className="h-8.5 w-8.25 bg-[#7D4B32] rounded-full flex items-center justify-center text-black/85 text-[19px]">
        {displayLabel}
      </div>
    </button>
  );
};

export default AccountButton;