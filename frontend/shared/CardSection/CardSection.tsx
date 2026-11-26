import SectionTitle from "../SectionTitle/SectionTitle";
import CardSlider from "../CardSlider/CardSlider";
import TrackCardSlider from "../TrackCardSlider/TrackCardSlider";

import { Song } from "@/redux/features/playerSlice";
import { Artist } from "@/redux/services/artistApislice";

export interface CardSectionProps<T> {
  title: string;
  items: T[];
  variant?: "track" | "artist";
  variant2?: "trending" | "freshtrack";
}

const CardSection = <T,>({
  title,
  items,
  variant = "artist",
  variant2,
}: CardSectionProps<T>) => {
  return (
    <section className="pt-5.75 grid gap-3 relative overflow-hidden">
      <SectionTitle title={title} />

      {variant === "track" ? (
        <TrackCardSlider
          cardimages={items as Song[]}
          title={title}
          variant="track"
          variant2={variant2}
        />
      ) : (
        <CardSlider
          cardimages={items as Artist[]}
          title={title}
        />
      )}
    </section>
  );
};

export default CardSection;