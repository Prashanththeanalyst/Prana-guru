export const ChatBubble = ({ type, content, timestamp }) => {
  const isUser = type === "user";
  
  return (
    <div
      className={`message-bubble ${isUser ? "message-user" : "message-guru"}`}
      data-testid={`message-${type}`}
    >
      <p className="whitespace-pre-wrap">{content}</p>
      {timestamp && (
        <span className="message-time">{timestamp}</span>
      )}
    </div>
  );
};
