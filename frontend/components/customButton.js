import { StyleSheet, Text, Pressable } from "react-native";

export default function CustomButton(props) {
  const { onPress, title = "Click", } = props;
  return (
    <Pressable
      style={({ pressed }) => [
        {
          backgroundColor: pressed ? "grey" : "black",
        },
        styles.button,
      ]}
      onPress={onPress}
    >
      <Text style={styles.text}>{title}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    alignItems: "center",
    justifyContent: "center",
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 4,
    elevation: 3,
  },
  text: {
    fontSize: 16,
    lineHeight: 21,
    fontWeight: "bold",
    letterSpacing: 0.25,
    color: "white",
  },
});
