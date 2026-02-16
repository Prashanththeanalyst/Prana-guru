export const ShlokaCard = ({ sanskrit, translation, source }) => {
  return (
    <div className="shloka-card max-w-[85%] md:max-w-[70%]" data-testid="shloka-card">
      {sanskrit && (
        <p className="shloka-sanskrit font-scripture">{sanskrit}</p>
      )}
      {translation && (
        <p className="shloka-translation">{translation}</p>
      )}
      {source && (
        <p className="shloka-source">— {source}</p>
      )}
    </div>
  );
};
